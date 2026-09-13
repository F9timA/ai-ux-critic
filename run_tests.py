from analyze import analyze_screenshot
import glob
import json
import os

def run_batch_test():
    image_files = glob.glob("test_screenshots/*.png") + glob.glob("test_screenshots/*.jpg") + glob.glob("test_screenshots/*.jpeg")

    if not image_files:
        print("No images found in test_screenshots/. Add some screenshots first.")
        return

    os.makedirs("test_results", exist_ok=True)

    for image_path in image_files:
        filename = os.path.basename(image_path)
        print(f"\n{'='*60}")
        print(f"Testing: {filename}")
        print('='*60)

        try:
            result = analyze_screenshot(image_path)
            issues = result.get("issues", [])

            print(f"Found {len(issues)} issue(s):\n")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. [{issue.get('severity', '?').upper()}] {issue.get('heuristic_violated', '')}")
                print(f"     Why: {issue.get('explanation', '')}")
                print(f"     Location: {issue.get('location_in_image', '')}")
                print(f"     Fix: {issue.get('suggested_fix', '')}\n")

            # Save each result to its own JSON file for later review
            result_filename = f"test_results/{os.path.splitext(filename)[0]}.json"
            with open(result_filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

        except Exception as e:
            print(f"ERROR analyzing {filename}: {e}")

    print(f"\n{'='*60}")
    print(f"Done. Tested {len(image_files)} images. Results saved in test_results/")
    print('='*60)


if __name__ == "__main__":
    run_batch_test()