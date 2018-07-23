from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from pykalman import KalmanFilter
import numpy as np
import requests

app=Flask(__name__)
app.config['DEBUG']=True
api=Api(app)

def FilteringStage(data):
	initial_state_mean=filter(lambda x: (x > 1) and (x <= 60),data)[0]
	transition_matrix=[1]
	observation_matrix=[1]	
	sensor_mask=np.ma.asarray(data)
	for i in range(0,len(data)):
		if data[i]<=1 or data[i]>=60:
			sensor_mask[i]=np.ma.masked
	
	kf=KalmanFilter(transition_matrices = transition_matrix, observation_matrices = observation_matrix, initial_state_mean = initial_state_mean,
				transition_covariance=0.05,observation_covariance=0.35)
	
	#for j in range(1,2):	#Se realizan hasta 10 filtros
	state_means, state_covs = kf.filter(sensor_mask)		#Ejecuta el filtro de kalman
		#sensor=state_means#sensor[indices[k]]=state_means[:,0][indices[k]]	#Modifica los 0 y 100 por los valores del filtro
	
	return state_means[:,0]

class KFilter(Resource):
	less_web="https://api.lessindustries.com/v1/messages/"

	def get(self):
		print "Stating"
		global less_web
		less_id=request.args.get('less_id')
		from_date=request.args.get('from_date')
		to_date=request.args.get('to_date')
		limit=request.args.get('limit')
		#params=dict(fromdate=from_date,todate=to_date,lessid=less_id,limit=limit)
		params='?from_date='+from_date+'&to_date='+to_date+'&less_id='+less_id+'&limit='+limit
		#response=requests.get(url=self.less_web,params=params,headers={'Authorization': 'token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjY1NjIxNTQsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNTU4MDk4MTU0LCJ1c2VybmFtZSI6Imphbm5pcm9jdkBnbWFpbC5jb20ifQ.3792hPpxX0KHW_Q9ajICvWd3jrLE785lKWiD-Mt1kKs'})
		response=requests.get(self.less_web+params, headers={'Authorization': 'token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjY1NjIxNTQsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNTU4MDk4MTU0LCJ1c2VybmFtZSI6Imphbm5pcm9jdkBnbWFpbC5jb20ifQ.3792hPpxX0KHW_Q9ajICvWd3jrLE785lKWiD-Mt1kKs'})
		raw_data=response.json()

		#print raw_data
		
		measurements=[]

		for x in raw_data:
			measurements.append([x['soil_vwc_1']['derived'],x['soil_vwc_2']['derived'],x['soil_vwc_3']['derived']])			

		#print len(measurements[0])

		soil1=[float(x[0]) for x in measurements]
		soil2=[float(x[1]) for x in measurements]
		soil3=[float(x[2]) for x in measurements]

		soft_soil1=FilteringStage(soil1)
		soft_soil2=FilteringStage(soil2)
		soft_soil3=FilteringStage(soil3)

		for pointer in range(len(raw_data)):
			raw_data[pointer]['soil_vwc_1']['derived']=soft_soil1[pointer]
		 	raw_data[pointer]['soil_vwc_2']['derived']=soft_soil2[pointer]
		 	raw_data[pointer]['soil_vwc_3']['derived']=soft_soil3[pointer]
		
		return raw_data

api.add_resource(KFilter,"/data")

if __name__=='__main__':
	app.run(port=5000)
		

