import os
import json
import subprocess
from typing import Dict, List

class ManimRenderer:
    def __init__(self, storyboard_path: str = "data/storyboard.json"):
        self.storyboard_path = storyboard_path
        loaded = self._load_storyboard()
        self.storyboard = self._normalize_storyboard(loaded)
        self.scene_file_path = "scenes/generated_scene.py"
    
    def _load_storyboard(self) -> dict:
        """Load the storyboard JSON."""
        with open(self.storyboard_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _normalize_storyboard(self, storyboard: dict) -> dict:
        """Normalize different storyboard formats into a standard dict with a 'scenes' list.

        Some tools embed a full storyboard JSON as a string inside the first scene's
        `description`. Detect and parse that format so downstream code can rely on
        a consistent structure.
        """
        scenes = storyboard.get("scenes", [])
        # If the first item contains a JSON-encoded storyboard in 'description', try to parse it
        if isinstance(scenes, list) and len(scenes) == 1:
            first = scenes[0]
            desc = first.get("description", "")
            if isinstance(desc, str) and ("\"scenes\"" in desc or "\"scene_id\"" in desc or desc.strip().startswith("{")):
                try:
                    parsed = json.loads(desc)
                    if isinstance(parsed, dict) and "scenes" in parsed and isinstance(parsed["scenes"], list):
                        # Merge meta fields like title/description if present
                        merged = parsed
                        if "title" not in merged and "title" in storyboard:
                            merged["title"] = storyboard.get("title")
                        if "description" not in merged and "description" in storyboard:
                            merged["description"] = storyboard.get("description")
                        return merged
                except json.JSONDecodeError:
                    # Not parseable JSON; fall back to original
                    pass
        return storyboard

    def _generate_scene_code(self) -> str:
        """Generate Python code for the Manim scene based on storyboard."""
        code = """from manim import *

class GeneratedScene(Scene):
    def construct(self):
"""

        scenes = self.storyboard.get("scenes", [])
        for i, scene in enumerate(scenes, start=1):
            scene_id = scene.get("scene_id", scene.get("id", i))
            narration = scene.get("narration", scene.get("description", ""))
            # Sanitize narration so multi-line or large content doesn't inject raw text into the generated Python
            safe_narration = (narration or "").replace("\n", " ").replace("\r", " ")
            code += f"\n        # Scene {scene_id}: {safe_narration[:70]}...\n"

            # Generate code for each element
            element_vars = []
            elements = scene.get("elements", [])
            for idx, element in enumerate(elements):
                var_name = f"elem_{scene_id}_{idx}"
                element_vars.append(var_name)

                # Create the element
                code += self._create_element_code(var_name, element)

            # Animate the elements
            if element_vars:
                animations = []
                for j, element in enumerate(elements):
                    var_name = element_vars[j]
                    anim = element.get("animation", "FadeIn")
                    animations.append(f"{anim}({var_name})")

                code += f"        self.play({', '.join(animations)})\n"

                # Wait for scene duration
                duration = scene.get("duration", 3)
                wait_time = max(0, duration - 1)
                code += f"        self.wait({wait_time})\n"

                # Fade out at the end of the scene
                code += f"        self.play({', '.join([f'FadeOut({v})' for v in element_vars])})\n"

        code += "        self.wait(1)\n"
        return code
    
    def _create_element_code(self, var_name: str, element: dict) -> str:
        """Generate code to create a single element."""
        code = ""
        elem_type = element.get("type", "text")
        content = element.get("content", "")
        position = list(element.get("position", [0, 0, 0]))
        color = element.get("color", "WHITE")
        scale = element.get("scale", 1.0)
        
        # Ensure position has 3 elements
        if len(position) == 2:
            position.append(0)
        
        # Prepare content literal safely (JSON encoding produces a valid Python string literal)
        content_literal = json.dumps(content)
        # Determine color literal: use unquoted identifier if it looks like a Manim color constant (UPPERCASE), else quote it
        color_literal = color if isinstance(color, str) and color.isupper() else json.dumps(color)
        
        # Create the element based on type
        if elem_type == "text":
            code += f"        {var_name} = Text({content_literal})\n"
        elif elem_type == "equation":
            code += f"        {var_name} = MathTex({content_literal})\n"
        elif elem_type == "circle":
            code += f"        {var_name} = Circle()\n"
        elif elem_type == "square":
            code += f"        {var_name} = Square()\n"
        elif elem_type == "arrow":
            code += f"        {var_name} = Arrow(start=LEFT, end=RIGHT)\n"
        elif elem_type == "line":
            code += f"        {var_name} = Line(start=LEFT, end=RIGHT)\n"
        elif elem_type == "axes":
            code += f"        {var_name} = Axes()\n"
        elif elem_type == "graph":
            code += f"        {var_name} = Axes()\n"
        else:
            # Use a safe string literal for unknown element text
            unknown_literal = json.dumps("Unknown element")
            code += f"        {var_name} = Text({unknown_literal})\n"
        
        # Apply properties
        code += f"        {var_name}.set_color({color_literal})\n"
        code += f"        {var_name}.scale({scale})\n"
        code += f"        {var_name}.move_to([{position[0]}, {position[1]}, {position[2]}])\n"
        
        return code
    
    def generate_scene_file(self):
        """Generate the scene Python file."""
        code = self._generate_scene_code()
        with open(self.scene_file_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Scene file generated: {self.scene_file_path}")
    
    def render_video(self, quality: str = "l", output_dir: str = "media"):
        """
        Render the video using Manim.
        
        Args:
            quality: Quality setting (l=low, m=medium, h=high, k=4k)
            output_dir: Output directory for the video
        """
        self.generate_scene_file()
        
        # Construct manim command
        cmd = [
            "manim",
            "-q" + quality,
            self.scene_file_path,
            "GeneratedScene"
        ]
        
        if output_dir:
            cmd.extend(["-o", output_dir])
        
        print(f"Rendering video with command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Video rendered successfully!")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error rendering video: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False
    
    def get_video_info(self) -> dict:
        """Get information about the video that will be generated."""
        scenes = self.storyboard.get("scenes", [])
        total_duration = sum(scene.get("duration", 3) for scene in scenes)
        return {
            "title": self.storyboard.get("title", "Untitled"),
            "description": self.storyboard.get("description", ""),
            "num_scenes": len(scenes),
            "total_duration": total_duration
        }