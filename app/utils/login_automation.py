# import asyncio
# from playwright.async_api import async_playwright
# # from app.utils.celery_task.celery_beat_configuration import app
#
# user_id = "90296TECH"
# membercode = "90296"
# password1 = "Neowealth@567"
#
#
# async def capture_initial_network_calls():
#     try:
#         capcha_response = {"capcha": None}
#
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(channel='chrome',headless=False,devtools=True)
#             context = await browser.new_context()
#             page = await context.new_page()
#
#             # Capture CAPTCHA from network response
#             async def log_response(response):
#                 if "generateCaptcha" in response.url:
#                     capcha_text = await response.text()
#                     cleaned_captcha = capcha_text.replace(" ", "").strip()
#                     capcha_response["capcha"] = cleaned_captcha
#                     print(f"Extracted CAPTCHA: {capcha_response['capcha']}")
#
#             page.on("response", log_response)
#
#             # Open the login page
#             await page.goto("https://ims.connect2nsccl.com/MemberPortal/")
#             await asyncio.sleep(5)  # Allow CAPTCHA to load
#
#             if not capcha_response["capcha"]:
#                 raise Exception("CAPTCHA not extracted. Check network request.")
#
#             # Fill login details
#             await page.fill('input[name="userid"]', user_id)
#             await asyncio.sleep(3)
#             await page.fill('input[name="membercode"]', membercode)
#             await asyncio.sleep(3)
#             await page.fill('input[name="password1"]', password1)
#             await asyncio.sleep(3)
#             await page.fill('input[id="UserCaptchaCode"]', capcha_response["capcha"])
#             await asyncio.sleep(3)
#
#             # Ensure CAPTCHA is set
#             captcha_input = await page.locator('input[id="UserCaptchaCode"]').input_value()
#             if not captcha_input.strip():
#                 raise Exception("CAPTCHA field is empty. Check extraction process.")
#
#             # Ensure the button is ready
#             await page.wait_for_selector("button.a2", state="visible", timeout=30000)
#
#             # Run JavaScript functions before clicking
#             await page.evaluate("generateSalt(); encryptPassword();")
#             captcha_valid = await page.evaluate("verifyCaptcha();")
#
#             if not captcha_valid:
#                 raise Exception("CAPTCHA verification failed. Check CAPTCHA extraction.")
#
#
#             # Check if login was successful
#             await asyncio.sleep(3)  # Wait for possible errors
#             if "login" in page.url.lower():
#                 error_message = await page.locator("div.error-message").text_content()
#                 raise Exception(f"Login failed: {error_message}")
#
#             await page.wait_for_load_state("domcontentloaded")
#
#             # Ensure correct page is loaded
#             await page.wait_for_function("window.location.href.includes('mainMenu')", timeout=100000)
#
#
#             # Ensure dashboard elements appear
#             await page.wait_for_selector("div.dashboard", timeout=20000)
#
#             print("Login Successful!")
#
#             # Pause for debugging
#             await page.pause()
#
#             await browser.close()
#     except Exception as exp:
#         print(f"Error: {exp}")
#
#
#
#
#
# @app.task
# def capture_initial_network_calls_sync():
#     asyncio.run(capture_initial_network_calls())
#
# # capture_initial_network_calls_sync()
#
# # encSaltC: iSVVXEo0OCtazcQIUBlG
# # userid: 90296TECH
# # membercode: 90296
# # password: eKX46NzEPD+2Y7CBZiFR/w==
# # encrPassMD5: 88a55a608d4cb6e3a2f75682d51b474d
# # encrSaltPassMD5: 9c4acfb216fdd381ac540e8d2092affb
# # encrPassSHA: 4136311331c758b9e999fe6f0ebd0a3308365e3a82900701dd3fc48de0659131
# # encrSaltPassSHA: 643b407f4b4b938fb267cc2556baef91c4b74b0b6f42bca0651dce38d0ec0d73
# # captchaCode: captchaCode
# # UserCaptchaCode1: LL@JWP
# #
# # encSaltC: XHZKCQ5AqilM38kqmQi0
# # userid: 90296TECH
# # membercode: 90296
# # password: eKX46NzEPD+2Y7CBZiFR/w==
# # encrPassMD5: 88a55a608d4cb6e3a2f75682d51b474d
# # encrSaltPassMD5: 9c4acfb216fdd381ac540e8d2092affb
# # encrPassSHA: 4136311331c758b9e999fe6f0ebd0a3308365e3a82900701dd3fc48de0659131
# # encrSaltPassSHA: 643b407f4b4b938fb267cc2556baef91c4b74b0b6f42bca0651dce38d0ec0d73
# # captchaCode: captchaCode
# # UserCaptchaCode1: xHWPTc