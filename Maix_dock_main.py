from fpioa_manager import fm
from machine import UART
from board import board_info
import time
import sensor
import image
from Maix import GPIO
from fpioa_manager import fm
# need your connect hardware IO 10/11 to loopback
fm.register(board_info.WIFI_TX, fm.fpioa.UART1_TX, force=True)
fm.register(board_info.WIFI_RX, fm.fpioa.UART1_RX, force=True)

uart = UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

green_threshold = (15, 73, -63, -12, 15, 45)
margin = 40

print (board_info)
while True:

    read_data = uart.read()
    if read_data:
        print("recv:\n", read_data.decode())

    img=sensor.snapshot()
    blobs = img.find_blobs([green_threshold], area_threshold=150)

    big_blob = None
    if blobs:
        for b in blobs:
            if big_blob:
                if b.pixels()>big_blob.pixels():
                    big_blob=b
            else:
                big_blob=b

    if big_blob:
        tmp=img.draw_rectangle(big_blob[0:4])
        tmp=img.draw_cross(big_blob[5], big_blob[6])
        c=img.get_pixel(big_blob[5], big_blob[6])
        err = abs(big_blob.x()+(big_blob.w()/2) - 320/2)
        if big_blob.x()+(big_blob.w()/2)>320/2+margin:

            uart.write('r'+str(err)+'\n')
        elif big_blob.x()+(big_blob.w()/2)<320/2-margin:
            uart.write('l'+str(err)+'\n')
        else:
            uart.write('f\n')
    else:
        uart.write('s\n')

uart.deinit()
del uart
