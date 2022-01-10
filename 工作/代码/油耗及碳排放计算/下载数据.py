import pyautogui
import time

'''
Point(x=107, y=328) 新增任务
Point(x=302, y=324) 车辆数据
Point(x=303, y=350) 发动机数据
Point(x=655, y=290) 任务名称
Point(x=748, y=347) 上传
Point(x=335, y=601) 桌面
Point(x=484, y=625) 模板位置
Point(x=956, y=892) 打开按钮
Point(x=730, y=399) 选择时间
Point(x=486, y=454) 开始时间
Point(x=812, y=455) 结束时间
Point(x=1006, y=822) 确定
Point(x=674, y=715) 保存
定义一个函数，传入对应的参数就可以了
需要传入的参数有 车辆数据位置，或者名称，起止日期，编号
name, index, start, end
'''
pyautogui.PAUSE = 0.25


def auto_download(name, index, start, end):
    pyautogui.click(x=107, y=328, duration=0.25, button='left')  # 新增任务
    time.sleep(1)
    pyautogui.click(x=302, y=324, duration=0.25, button='left')  # 车辆数据
    pyautogui.click(x=303, y=350, duration=0.25, button='left')  # 发动机数据
    pyautogui.click(x=655, y=290, duration=0.25, button='left')  # 任务名称
    pyautogui.write(name + str(index))  #
    pyautogui.click(x=748, y=347, duration=0.25, button='left')  # 上传
    pyautogui.click(x=344, y=590, duration=0.25, button='left')  # 桌面
    pyautogui.click(x=591, y=578, duration=0.25, button='left')  # 模板位置
    pyautogui.click(x=956, y=892, duration=0.25, button='left')  # 打开按钮
    pyautogui.click(x=730, y=399, duration=0.25, button='left')  # 选择时间
    pyautogui.click(x=486, y=454, duration=0.25, button='left')  # 开始时间
    for i in range(10):
        pyautogui.press('backspace')
    pyautogui.write(start)
    pyautogui.click(x=731, y=509, duration=0.25, button='left')
    pyautogui.click(x=731, y=509, duration=0.25, button='left')
    time.sleep(0.25)
    pyautogui.click(x=812, y=455, duration=0.25, button='left')  # 结束时间

    time.sleep(2)
    for i in range(10):
        pyautogui.press('backspace')
    pyautogui.write(end)
    pyautogui.click(x=731, y=509, duration=0.25, button='left')
    pyautogui.click(x=731, y=509, duration=0.25, button='left')
    time.sleep(0.25)
    pyautogui.click(x=731, y=509, duration=0.25, button='left')
    pyautogui.click(x=1006, y=822, duration=0.25, button='left')  # 确定
    time.sleep(0.25)
    pyautogui.click(x=674, y=715, duration=0.25, button='left')  # 保存
    time.sleep(5)
    return


# auto_download('zidongceshi', 5, '2021 - 1 - 1', '2021 - 2 - 1')
# upload_button = pyautogui.locateOnScreen('upload.png', grayscale=True)
# upload_button_center = pyautogui.center(upload_button)
# x, y = upload_button_center
# print(x, y)
# pyautogui.moveTo(x, y)
# pyautogui.click(x, y)
# pyautogui.click(x, y)

pyautogui.click(x=107, y=335, duration=0.25, button='left')
for i in range(11):
    start = '2021-'+ str(i + 1) + '-1'
    end = '2021-' + str(i + 2) + '-1'
    auto_download('guangxi', i + 1, start, end)
