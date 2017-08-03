from __future__ import print_function
import torch

import DatasetLoader as DL
import CNNNetwork as testnetwork

batch_size = 64

#############################################
######### DATA LOADING ######################
#############################################

loader = DL.Loader()
train, test = loader.generateTensorDatasetFromMNISTFolder('../data/MNIST/')
train_loader = torch.utils.data.DataLoader(train, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(train, batch_size=batch_size, shuffle=True)

testnet = testnetwork.TestingNetwork()
testnet.setData(train_loader, test_loader)

#############################################
######### TRAINING AND TESTING ##############
#############################################

#for epoch in range(1):
#	testnet.train(epoch + 1)
#	pass

testnet.loadModelFromFile('model/version1.mdl')
testnet.test()

print (testnet.conv1)

#testnet.saveModelToFile('model/version1.mdl')