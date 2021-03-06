import torch
import torchvision
import torch.optim as optim
import torch.nn as nn
import torchvision.transforms as transforms
from torch.utils import data
from model import studentNet,teacherNet

torch.manual_seed(123)


class MNIST(data.Dataset):
    urls = [
        '/home/lchen/Model-Compression-For-Speaker-Recognition/Model_Compression/knowledgeDistillation/example/data/MNIST/raw/t10k-labels-idx1-ubyte.gz',
        '/home/lchen/Model-Compression-For-Speaker-Recognition/Model_Compression/knowledgeDistillation/example/data/MNIST/raw/train-labels-idx1-ubyte.gz',
        '/home/lchen/Model-Compression-For-Speaker-Recognition/Model_Compression/knowledgeDistillation/example/data/MNIST/raw/t10k-images-idx3-ubyte.gz',
        '/home/lchen/Model-Compression-For-Speaker-Recognition/Model_Compression/knowledgeDistillation/example/data/MNIST/raw/t10k-labels-idx1-ubyte.gz',
    ]               
                                                                                                                                                                

transform = transforms.Compose(
    [transforms.ToTensor()])

trainset = torchvision.datasets.MNIST(root='./data', train=True,
                                        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=10,
                                          shuffle=True, num_workers=2)

testset = torchvision.datasets.MNIST(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=10,
                                         shuffle=False, num_workers=2)

device =  torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
Loss = nn.CrossEntropyLoss()

# Train Student Net Without Teacher
print("Start training student net alone")
student = studentNet().to(device)
optimizer = optim.SGD(student.parameters(), lr=0.001, momentum=0.9)

for epoch in range(2):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, batch in enumerate(trainloader, 0):
        # get the inputs
        inputs, labels = batch
        inputs = inputs.to(device)
        labels = labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = student(inputs)
        loss = Loss(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % 2000 == 1999:    # print every 2000 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 2000))
            running_loss = 0.0

print('Student Finished Training')

# Eval Student
correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data
        images = images.to(device)
        labels = labels.to(device)
        outputs = student(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(correct)
print('Accuracy of the student network without teacher on the 10000 test images:',correct/total)





# Train Teacher Net 
print("Start training teacher net ")
teacher = teacherNet().to(device)
optimizer = optim.SGD(teacher.parameters(), lr=0.001, momentum=0.9)

for epoch in range(2):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, batch in enumerate(trainloader, 0):
        # get the inputs
        inputs, labels = batch
        inputs = inputs.to(device)
        labels = labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = teacher(inputs)
        loss = Loss(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % 2000 == 1999:    # print every 2000 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 2000))
            running_loss = 0.0

print('Teacher Finished Training')

# Eval Student
correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data
        images = images.to(device)
        labels = labels.to(device)
        outputs = teacher(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(correct)
print('Accuracy of the teacher networkon the 10000 test images:',correct/total)

torch.save(teacher.state_dict(), 'teacher.pth')

