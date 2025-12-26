#!/usr/bin/env python3
"""
3Blue1Brown Style Video Generator
Converts transcript to animated educational videos using Manim
"""

import argparse
import sys
from agents import StoryboardAgent
from renderer import ManimRenderer

def main():
    parser = argparse.ArgumentParser(
        description="Generate 3Blue1Brown-style videos from transcripts"
    )
    
    parser.add_argument(
        "--transcript",
        type=str,
        help="Direct transcript text (overrides file input)"
    )
    
    parser.add_argument(
        "--transcript-file",
        type=str,
        default="input/transcript.txt",
        help="Path to transcript file (default: input/transcript.txt)"
    )
    
    parser.add_argument(
        "--storyboard",
        type=str,
        default="data/storyboard.json",
        help="Path to save/load storyboard JSON (default: data/storyboard.json)"
    )
    
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip storyboard generation and use existing storyboard"
    )
    
    parser.add_argument(
        "--quality",
        type=str,
        choices=["l", "m", "h", "k"],
        default="m",
        help="Video quality: l(low), m(medium), h(high), k(4k) - default: m"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="media",
        help="Output directory for rendered video (default: media)"
    )
    
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate storyboard, don't render video"
    )
    
    args = parser.parse_args()
    
    # Get transcript
    transcript = None
    if args.transcript_file:
        try:
            with open(args.transcript_file, "r", encoding="utf-8") as f:
                transcript = f.read()
        except FileNotFoundError:
            print(f"Error: Transcript file not found: {args.transcript_file}")
            sys.exit(1)
    elif args.transcript:
        transcript = args.transcript
    elif not args.skip_generation:
        print("Error: Please provide a transcript using --transcript or --transcript-file")
        parser.print_help()
        sys.exit(1)
    
    # Step 1: Generate or load storyboard
    if not args.skip_generation:
        print("\n" + "="*60)
        print("STEP 1: Generating Storyboard")
        print("="*60)
        
        agent = StoryboardAgent()
        try:
            storyboard = agent.generate_storyboard(transcript)
            agent.save_storyboard(storyboard, args.storyboard)
            
            print(f"\nStoryboard Summary:")
            print(f"  Title: {storyboard.get('title', 'N/A')}")
            print(f"  Number of scenes: {len(storyboard.get('scenes', []))}")
            
        except Exception as e:
            print(f"Error generating storyboard: {e}")
            sys.exit(1)
    else:
        print("\n" + "="*60)
        print("STEP 1: Loading Existing Storyboard")
        print("="*60)
        print(f"Loading storyboard from: {args.storyboard}")
    
    if args.generate_only:
        print("\nStoryboard generation complete. Skipping video rendering.")
        return
    
    # Step 2: Render video
    print("\n" + "="*60)
    print("STEP 2: Rendering Video with Manim")
    print("="*60)
    
    try:
        renderer = ManimRenderer(args.storyboard)
        
        # Show video info
        info = renderer.get_video_info()
        print(f"\nVideo Information:")
        print(f"  Title: {info['title']}")
        print(f"  Description: {info['description']}")
        print(f"  Number of scenes: {info['num_scenes']}")
        print(f"  Estimated duration: {info['total_duration']} seconds")
        print(f"  Quality: {args.quality}")
        
        # Render
        print("\nStarting render...")
        success = renderer.render_video(quality=args.quality, output_dir=args.output)
        
        if success:
            print("\n" + "="*60)
            print("SUCCESS! Video rendered successfully")
            print("="*60)
            print(f"Check the '{args.output}' directory for your video")
        else:
            print("\n" + "="*60)
            print("ERROR: Video rendering failed")
            print("="*60)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error rendering video: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()