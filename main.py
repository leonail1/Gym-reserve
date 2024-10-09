import time
from typing import Union

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchWindowException


def attempt_login(driver, url, username, password, timeout=30):
    try:
        # 访问登录页面
        driver.get(url)

        # 首先等待 body 元素加载完成
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # 检查是否已经登录
        try:
            expected_text = "本系统仅供在校师生使用，不得在体育场馆进行其他无关的活动。"
            WebDriverWait(driver, 2).until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="block-block-1"]/p[1]'), expected_text)
            )
            print("已经处于登录状态，检测到预期文本内容。")
            return True
        except TimeoutException:
            # 如果没有检测到预期文本，则继续登录流程
            pass

        # 等待并填写用户名
        username_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="user_name"]'))
        )
        username_input.send_keys(username)

        time.sleep(0.5)

        # 填写密码
        password_input = driver.find_element(By.XPATH, '//*[@id="form"]/div[3]/div/input')
        password_input.send_keys(password)

        time.sleep(0.5)

        # 点击登录按钮
        login_button = driver.find_element(By.XPATH, '//*[@id="login"]')
        login_button.click()

        # 等待特定文本内容出现，表示页面加载完成
        WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element((By.XPATH, '//*[@id="block-block-1"]/p[1]'), expected_text)
        )

        print("登录成功，已检测到预期文本内容。")
        return True
    except TimeoutException:
        print("登录失败或页面加载超时。")
        return False


class BrowserClosedException(Exception):
    """自定义异常，表示浏览器已被关闭"""
    pass


def navigate_with_retry(driver, url, wait_element, max_retries=3, retry_delay=5):
    retry_count = 0
    while True:
        try:
            retry_count += 1
            print(f"尝试导航到页面 {url} (第 {retry_count} 次)")

            driver.get(url)
            element_present = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(wait_element)
            )
            if element_present:
                print(f"已成功打开页面: {url}")
                return True
            else:
                print("未检测到特定元素，将重试。")
                raise Exception("未检测到特定元素")

        except NoSuchWindowException:
            print("浏览器窗口已被关闭。")
            raise BrowserClosedException("浏览器窗口已被关闭")
        except TimeoutException:
            print(f"页面加载超时 (尝试 {retry_count}/{max_retries})")
        except Exception as e:
            print(f"发生其他错误 (尝试 {retry_count}/{max_retries}): {e}")

        if retry_count >= max_retries:
            print(f"达到最大重试次数 ({max_retries})。操作失败。")
            return False

        print(f"等待 {retry_delay} 秒后重试...")
        time.sleep(retry_delay)


def perform_login(driver, username, password):
    try:
        # 定位并填写用户名
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
        )
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(0.5)

        # 定位并填写密码
        password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(0.5)

        # 点击登录按钮
        login_button = driver.find_element(By.XPATH, '//*[@id="login_submit"]')
        login_button.click()

        print("登录操作完成")
        return True

    except NoSuchWindowException:
        print("浏览器窗口已被关闭。")
        raise BrowserClosedException("浏览器窗口已被关闭")

    except TimeoutException:
        print("等待元素超时")
        return False

    except Exception as e:
        print(f"登录过程中出现其他错误: {e}")
        return False


def automated_login(student_id, password, fitness_or_swimming, reserve_date, reserve_time: list,
                    max_retries=(2 << 63) - 1,
                    retry_delay=3):
    url = "https://cgyy.xmu.edu.cn/"  # 请替换为实际的登录页面URL
    username = student_id

    time_to_index = {
        "swimming": {
            "09:30-11:00": 5,
            "12:00-14:00": 4,
            "14:30-16:00": 1,
            "16:30-18:00": 2,
            "18:30-20:30": 3,
        },
        "fitness": {
            "10:30-12:00": 16,
            "12:00-13:30": 10,
            "13:30-15:00": 11,
            "15:00-16:30": 12,
            "16:30-18:00": 13,
            "18:00-19:30": 14,
            "19:30-21:00": 15,
        }
    }

    if fitness_or_swimming == "游泳":
        fitness_or_swimming = "swimming"
    elif fitness_or_swimming == "健身":
        fitness_or_swimming = "fitness"

    reserve_time = [time_to_index[fitness_or_swimming][reserve_time[i]] for i in range(len(reserve_time))]

    for attempt in range(max_retries):
        print(f"执行第 {attempt + 1} 次尝试")
        driver = None
        try:
            edge_options = webdriver.EdgeOptions()
            edge_options.use_chromium = True
            driver = webdriver.Edge(options=edge_options)

            if not attempt_login(driver, url, username, password):
                raise Exception("登录失败")

            print("登录成功！")

            weixin_url = "http://ids.xmu.edu.cn/authserver/login?service=http://cgyy.xmu.edu.cn/idcallbac"
            username_password_url = "https://ids.xmu.edu.cn/authserver/login?type=userNameLogin&service=http%3A%2F%2Fcgyy.xmu.edu.cn%2Fidcallback"
            reserve_fitness_url = "https://cgyy.xmu.edu.cn/room/1"
            reserve_swimming_url = "https://cgyy.xmu.edu.cn/room/2"

            if not navigate_with_retry(driver, weixin_url, (By.XPATH, '//*[@id="userNameLogin_a"]'), 3, retry_delay):
                raise Exception("导航到厦大账号企业微信登录页面失败")
            print("成功导航到厦大账号企业微信登录页面")

            if not navigate_with_retry(driver, username_password_url, (By.XPATH, '//*[@id="username"]'), 3,
                                       retry_delay):
                raise Exception("导航到厦大账号账密登录页面失败")
            print("成功导航到厦大账号账密登录页面")

            if not perform_login(driver, username, password):
                raise Exception("厦大账号登录操作失败")
            print("厦大账号登录操作成功完成")

            if fitness_or_swimming == "fitness":
                if not navigate_with_retry(driver, reserve_fitness_url, (By.XPATH, '//*[@id="page-title"]'), 3,
                                           retry_delay):
                    raise Exception("导航到健身房预约页面失败")
            elif fitness_or_swimming == "swimming":
                if not navigate_with_retry(driver, reserve_swimming_url, (By.XPATH, '//*[@id="page-title"]'), 3,
                                           retry_delay):
                    raise Exception("导航到游泳馆预约页面失败")
            else:
                raise ValueError("fitness_or_swimming变量只能选择预约健身房(fitness)或预约游泳馆(swimming)")

            reserve_done = False

            # 在这里添加预约操作的代码
            if fitness_or_swimming == "swimming":
                for current_reserve_time in reserve_time:
                    time_period_url = f"https://cgyy.xmu.edu.cn/room_apl/2/{reserve_date}/{current_reserve_time}/cg"
                    if not navigate_with_retry(driver, time_period_url, (By.XPATH, '/html/body'), 1, retry_delay):
                        raise Exception("导航到游泳馆预约填写电话界面失败")

                    try:
                        print(f"尝试预约游泳馆的{current_reserve_time}时间段")
                        input_phone_and_submit(driver)
                    except NoSuchElementException as e:
                        print(f"{current_reserve_time}:{str(e)}")
                        continue

                    print(f"预约游泳馆的{current_reserve_time}时间段成功！")
                    reserve_done = True
                    break
            else:
                for current_reserve_time in reserve_time:
                    time_period_url = f"https://cgyy.xmu.edu.cn/room_apl/1/{reserve_date}/{current_reserve_time}/cg"
                    if not navigate_with_retry(driver, time_period_url, (By.XPATH, '/html/body'), 1, retry_delay):
                        raise Exception("导航到健身房预约填写电话界面失败")

                    try:
                        print(f"尝试预约健身房的{current_reserve_time}时间段")
                        input_phone_and_submit(driver)
                    except NoSuchElementException as e:
                        print(f"{current_reserve_time}:{str(e)}")
                        continue

                    print(f"预约健身房的{current_reserve_time}时间段成功！")
                    reserve_done = True
                    break

            if reserve_done:
                print("所有操作成功完成！")
                return True
            else:
                print("所有时间段预约均失败。")

        except Exception as e:
            print(f"执行过程中出现错误: {e}")
            if isinstance(e, NoSuchWindowException) or isinstance(e, BrowserClosedException):
                print("浏览器被手动关闭，程序终止")
                return False

            if attempt < max_retries - 1:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print("达到最大重试次数。操作失败。")

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass  # 忽略关闭驱动程序时可能出现的错误

    return False


def input_phone_and_submit(driver, phone_number="17704675461"):
    try:
        # 查找电话号码输入框
        input_element = driver.find_element(By.XPATH, '//*[@id="edit-field-tel-und-0-value"]')

        # 输入电话号码
        input_element.clear()  # 清除可能存在的旧值
        input_element.send_keys(phone_number)

        # 等待0.5秒
        time.sleep(0.5)

        # 查找并点击提交按钮
        submit_button = driver.find_element(By.XPATH, '//*[@id="edit-submit"]')
        submit_button.click()

        return True  # 操作成功完成，返回False表示不需要进一步处理

    except NoSuchElementException:
        raise NoSuchElementException("未找到电话号码输入框或提交按钮，请检查所选时间段是否已被约满/未开放/已经预约成功。")


if __name__ == "__main__":
    # fitness_or_swimming = "swimming"
    # reserve_date = "2024-10-08"
    # reserve_time = ["09:30-11:00"]

    fitness_or_swimming = "fitness"
    reserve_date = "2024-10-12"
    reserve_time = ["10:30-12:00", "12:00-13:30", "13:30-15:00", "15:00-16:30"]

    automated_login("37220222203691", "mkbk.445566", fitness_or_swimming, reserve_date, reserve_time)
