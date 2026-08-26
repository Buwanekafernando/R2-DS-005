from utils.scarcity_agent import ScarcityAgent
from pathlib import Path

def run_batch_demo():
    agent = ScarcityAgent()
    base_dir = Path(__file__).parent
    input_file = base_dir / "dataset" / "sample_products.json"
    output_file = base_dir / "outputs" / "scarcity_results.json"
    
    if input_file.exists():
        print(f"Starting batch process on {input_file}...")
        agent.process_batch_from_json(str(input_file), str(output_file))
        print(f"Success! Check {output_file} for the output.")
    else:
        print(f"Dataset file not found at {input_file}. Run dataset_processor.py first to generate the sample.")

if __name__ == "__main__":
    run_batch_demo()
