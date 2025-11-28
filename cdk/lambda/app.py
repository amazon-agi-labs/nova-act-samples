def handler(event, context):
    print(f"Event - {event}")
    print(f"Context - {context}")
    
    nova_act(event)
    
    print("Done!")


def nova_act(event):
    from nova_act import NovaAct
    
    required_keys = ["prompts", "starting_page"]
    for required_key in required_keys:
        if event.get(required_key) is None:
            raise ValueError(f"Event JSON '{required_key}' is required")
    
    with NovaAct(
        chrome_channel="chromium",
        headless=True,
        starting_page=event.get("starting_page"),
    ) as nova_act:
        session_id = nova_act.get_session_id()
        print(f"Session ID - {session_id}")
        
        for prompt in event.get("prompts"):
            print(f"Prompt - {prompt}")
            nova_act.act(prompt)


def playwright():
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=["--disable-gpu", "--headless=new", "--single-process"],
            channel="chromium",
            headless=True,
        )
        page = browser.new_page()
        page.goto("https://www.google.com")
        browser.close()


if __name__ == "__main__":
    handler(None, None)
