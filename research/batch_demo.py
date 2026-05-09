from scarcity_agent import ScarcityAgent
import os

def run_batch_demo():
    agent = ScarcityAgent()
    input_file = "sample_products.json"
    output_file = "scarcity_results.json"
    
    if os.path.exists(input_file):
        print(f"Starting batch process on {input_file}...")
        agent.process_batch_from_json(input_file, output_file)
        print("Success! Check scarcity_results.json for the output.")
    else:
        print("Run dataset_processor.py first to generate the sample.")

if __name__ == "__main__":
    run_batch_demo()
