from scarcity_agent import ScarcityAgent

if __name__ == "__main__":
    agent = ScarcityAgent(api_key="local-training-key")
    print(f"Model path: {agent.model_path}")
    print(f"Model loaded: {agent.local_model is not None}")
    print(agent.determine_intensity(
        "Luxury smartwatch",
        "Premium wearable for modern lifestyles",
        product_info={"price": 899, "category": "tech"},
        pain_points=["Stock Instability", "Shipping Delays"]
    ))
