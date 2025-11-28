from nova_act import NovaAct

def main():
    prompt = "Navigate to the homepage and verify it loads successfully"
    
    print("Starting Nova Act Fargate workflow...")
    
    try:
        with NovaAct(
            starting_page="https://example.com",
            headless=True,
            record_video=False,
            clone_user_data_dir=False,
        ) as nova_act:
            print("Executing Nova Act workflow...")
            result = nova_act.act(prompt)
            print(f"Workflow completed successfully: {result}")
            
        print("Fargate task completed successfully")
        
    except Exception as e:
        print(f"Workflow failed: {e}")
        raise

if __name__ == "__main__":
    main()
