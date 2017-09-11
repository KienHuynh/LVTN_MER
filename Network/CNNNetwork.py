from __future__ import print_function
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import getGT
from torch.autograd import Variable
import numpy
numpy.set_printoptions(threshold=10000)

import WAP

import NetWorkConfig
import pdb

import matplotlib.pyplot as plt

class TestingNetwork:
	def __init__(self):
		print ('network init')
		self.all_loss = []
		self.ite = 0
		################################################
		########## ATTRIBUTE INIT ######################
		################################################
		self.using_cuda = False  
		self.batch_size = 64
		self.learning_rate = 0.0001
		self.momentum = 0.9
		self.lr_decay_base = 0#1/1.15
		
		self.model = WAP.WAP()

		#self.model = Net()
		#self.model = FCN()
		train_params = []
		for p in self.model.parameters(): 
			if (p.requires_grad):
				train_params.append(p)
				
		#self.optimizer = optim.SGD(train_params, lr=self.learning_rate, momentum=self.momentum,
		#					 weight_decay = self.lr_decay_base)
		
		self.optimizer = optim.Adam(train_params, lr=self.learning_rate)
		#self.optimizer = optim.SGD(self.model.parameters(), lr=self.learning_rate, momentum=self.momentum)
		self.NLLloss = nn.NLLLoss2d()
		self.NLLloss1 = nn.NLLLoss()
		
		if NetWorkConfig.CURRENT_MACHINE == 0:
			self.criterion = nn.CrossEntropyLoss(ignore_index=1)
		else:
			self.criterion = nn.CrossEntropyLoss()
		
	def grad_clip(self, max_grad = 0.01):
		params = [p for p in list(self.model.parameters()) if p.requires_grad==True]
		for p in params:
			p_grad = p.grad 
			if (type(p_grad) == type(None)):
				#pdb.set_trace()
				#here = 1
				pass
			else:
				magnitude = torch.sqrt(torch.sum(p_grad**2))  
				if (magnitude.data[0] > max_grad):
					p_grad.data = (max_grad*p_grad/magnitude.data[0]).data
					
					
					
	def try_print(self, print_flag = True):
		params = [p for p in list(self.model.parameters()) if p.requires_grad==True]
		for p in params:
			p_grad = p.grad 
			
			try:
				if print_flag:
					print ('exist')
					print (type(p_grad))
					print (p_grad.data.numpy().shape)
				else:
					print (p_grad.data.numpy())
					
			except:
				if print_flag:
					print ('non - exist')
					pass
			
			
	def setCudaState(self, state = True):
		self.using_cuda = state

		self.model.setCuda(state)
		
	def setData(self, train, test):
		self.train_loader = train
		self.test_loader = test
	
	def train(self, epoch):
		self.model.train()
		###################decay _learning_rate################
#		lr = self.learning_rate
#		lr_decay_base = 1/1.15
#		epoch_base = 70
#		lr_decay = lr_decay_base ** max(epoch - epoch_base, 0)
#		lr = lr * lr_decay

		for batch_idx, (data, target) in enumerate(self.train_loader):

			self.model.setGroundTruth(target.numpy())

			if self.using_cuda:
				data, target = data.cuda(), target.cuda()
				
			if (self.ite%5000 == 1999):
				self.learning_rate = self.learning_rate/1.5
				print("Current learning rate: %.8f" % self.learning_rate)
				self.optimizer.param_groups[0]['lr'] = self.learning_rate
				print(self.optimizer.param_groups[0]['lr'])
			data, target = Variable(data.float()), Variable(target.long())
			self.optimizer.zero_grad()
			output = self.model(data)
			
			#print('output', output)
			
			if True:
				#for b_id in range(NetWorkConfig.BATCH_SIZE):
				#	for s_id in range(50):
				#		if target.data[b_id, s_id] == getGT.word_to_id['$P']:
				#			target.data[b_id,s_id] = 0
				#			output.data[b_id,s_id, :] = 0
				#			output.data[b_id,s_id, 0] = 1
				#pdb.set_trace()			
				#target = target[:,0:49]
				target.contiguous()
				#output = output[:,0:50]
				output.contiguous()
				target = target.view(NetWorkConfig.BATCH_SIZE * NetWorkConfig.MAX_TOKEN_LEN)
				output = output.view(NetWorkConfig.BATCH_SIZE * NetWorkConfig.MAX_TOKEN_LEN, NetWorkConfig.NUM_OF_TOKEN)
					
			        

				#-------------------------------------------------

				loss = self.criterion(output, target)
				
			else :
				pass

			loss.backward()
			self.grad_clip()
			if (epoch % 20 == 0):
				pass
#				pdb.set_trace()
#			self.try_print();
			self.optimizer.step() 
			self.ite += 1
			if self.using_cuda:
				self.all_loss.append(loss.cpu().data.numpy())
			else:
				self.all_loss.append(loss.data.numpy())
			plt.ion()

			if batch_idx % 1 == 0:
#				print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
#						epoch, batch_idx * len(data), len(self.train_loader.dataset),
#						100. * batch_idx / len(self.train_loader), loss.data[0]))
				print('[E %d, I %d]: %.5f' % (epoch,self.ite, loss.data[0]))
				plt.clf()
				plt.plot(self.all_loss)
				plt.draw()
				if batch_idx > 1:
					pass
					#break
			#break
		
	
	def test(self):
		self.model.eval()

		
		for batch_idx, (data, target) in enumerate(self.train_loader):


			self.model.setGroundTruth(target.numpy())
			if self.using_cuda:
				print('using cuda', self.using_cuda)
				data, target = data.cuda(), target.cuda()

			data, target = Variable(data.float()), Variable(target.long())
			
			output = self.model(data)
			#print('output', output)
			

			target.contiguous()
			output.contiguous()

			target = target.view(NetWorkConfig.BATCH_SIZE * NetWorkConfig.MAX_TOKEN_LEN)
			output = output.view(NetWorkConfig.BATCH_SIZE * NetWorkConfig.MAX_TOKEN_LEN, NetWorkConfig.NUM_OF_TOKEN)

			#print ('------PTP DEBUG------------------');
			#print (target.view(1, NetWorkConfig.BATCH_SIZE * NetWorkConfig.MAX_TOKEN_LEN))
			#print(output.max(1)[1].view(1, NetWorkConfig.BATCH_SIZE * NetWorkConfig.MAX_TOKEN_LEN))				        

				#-------------------------------------------------
			self.ite += 1
			self.printTestResult(target, output)
			loss = self.criterion(output, target)
			


			if batch_idx % 1 == 0:
				print('[E %d, I %d]: %.5f' % (0,self.ite, loss.data[0]))
		
		

	def printTestResult(self,  target, predict):
		target = target.cpu().data.numpy()
		predict = predict.max(1)[1].cpu().data.numpy()

		#self.getSampleResult(target, predict, self.ite)

		for j in range(NetWorkConfig.BATCH_SIZE):
			print('')
			print ('Batch index: ' + str(j))
			for i in range(NetWorkConfig.MAX_TOKEN_LEN ):
				if ((target[i + j * NetWorkConfig.MAX_TOKEN_LEN] == 1) and (target[i + j * NetWorkConfig.MAX_TOKEN_LEN + 1] == 1)):
					break
				print ('%3s|' % target[i + j * NetWorkConfig.MAX_TOKEN_LEN], end='')
			print ('')
			for i in range(NetWorkConfig.MAX_TOKEN_LEN):
				if ((predict[i + j * NetWorkConfig.MAX_TOKEN_LEN] == 19) and (predict[i + j * NetWorkConfig.MAX_TOKEN_LEN + 1] == 19)):
					break
				print ('%3s|' % predict[i + j * NetWorkConfig.MAX_TOKEN_LEN], end='')
		pass

	def getSampleResult(self, target, predict, batch_id):
		numpy.save('./PTPsSample/target'  + str(batch_id), target)
		numpy.save('./PTPsSample/predict' + str(batch_id), predict)


	def saveModelToFile(self, path):
		torch.save(self.model.state_dict(), path)
	
	def loadModelFromFile(self, path):
		self.model.load_state_dict(torch.load(path))

		
