import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
import datetime
from django.shortcuts import render

def Homepage(request):
    now = datetime.datetime.now()
    subject = "Time is {}".format(now)
    return render(request,'Home.html', {'subject':subject})

def plot_view(request):
    fig, ax = plt.subplots()
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]
    ax.plot(x, y)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

def plotbar_view(request):
    fig, ax = plt.subplots()
    x = ['A', 'B', 'C', 'D', 'E']
    y = [7, 8, 4, 20, 17]
    ax.bar(x, y)  # เปลี่ยนจาก ax.plot เป็น ax.bar

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

def plotscatter_view(request):
    fig, ax = plt.subplots()
    x = [1, 2, 3, 4, 5]
    y = [5, 7, 9, 6, 4]
    ax.scatter(x, y)  # ใช้ scatter แทน plot หรือ bar

    ax.set_title('Scatter Plot Example')  # เพิ่มชื่อกราฟ
    ax.set_xlabel('X-axis')  # ชื่อแกน X
    ax.set_ylabel('Y-axis')  # ชื่อแกน Y

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

def plotpie_view(request):
    fig, ax = plt.subplots()
    sizes = [15, 30, 45, 10]
    labels = ['A', 'B', 'C', 'D']
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')  # ใช้ ax.pie

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')


