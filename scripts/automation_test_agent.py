from playwright.sync_api import sync_playwright, Playwright
import termo_agents


def run(playwright: Playwright):
    firefox = playwright.firefox
    browser = firefox.launch(headless=False, slow_mo=0)
    context = browser.new_context(
        record_video_dir="videos/",
    )
    page = context.new_page()

    paths = ['', '2', '4']
    agent = termo_agents.model_based_reflex_agent

    for i, path in enumerate(paths):
        page.goto(f"https://term.ooo/{path}")
        boards = page.locator('wc-board').count()
        attempt_count = int(page.locator('wc-board').first.get_attribute('rows'))
        histories = [list() for _ in range(boards)]
        print('boards:', boards)
        print('history:', histories)
        print('tentativas:', attempt_count)

        # Fechar a tela de tutorial
        page.keyboard.press("Escape")

        for attempt in range(attempt_count):
            guess = agent(histories)
            page.keyboard.type(guess)
            page.keyboard.press("Enter")
            page.wait_for_timeout(1400)


            for board_id in range(boards):
                table = page.locator(f'#board{board_id}')
                linha = table.locator(f'wc-row[termo-row="{attempt}"]')
                letras = linha.locator('.letter')

                if any(score == [1, 1, 1, 1, 1] for past_attempt in histories[board_id] for score in past_attempt.values()):
                    continue

                for letra in letras.all():
                    label = letra.get_attribute("aria-label")
                    print("label:", label)

                result = []
                for letra in letras.all():
                    label = letra.get_attribute("aria-label")
                    if 'correta' in label:
                        result.append(1)
                    elif 'errada' in label:
                        result.append(-1)
                    elif 'outro local' in label:
                        result.append(0)

                histories[board_id].append({guess: result})
                print(histories)

            if all(
                    any(score == [1, 1, 1, 1, 1] for past_attempt in history for score in past_attempt.values())
                    for history in histories
            ):
                break

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)