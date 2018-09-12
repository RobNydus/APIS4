from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from pykalman import KalmanFilter
import numpy as np
from scipy.interpolate import interp1d
import requests
import datetime

app=Flask(__name__)
api=Api(app)

def FilteringStage(data,clase=1):
	if clase==1:
		try:
			initial_state_mean=filter(lambda x: (x > 0) and (x <= 60),data)[0]
		except:
			initial_state_mean=0
		sensor_mask=np.ma.asarray(data)
		for i in range(0,len(data)):
			if data[i]<=0.1 or data[i]>=61:
				sensor_mask[i]=np.ma.masked
	elif clase==2:
		try:
			initial_state_mean=filter(lambda x: (x > 0) and (x < 100),data)[0]
		except:
			initial_state_mean=0
		sensor_mask=np.ma.asarray(data)
		for i in range(0,len(data)):
			if data[i]<=0.01 or data[i]>=61:
				sensor_mask[i]=np.ma.masked

	transition_matrix=[1]
	observation_matrix=[1]	
	
	
	kf=KalmanFilter(transition_matrices = transition_matrix, observation_matrices = observation_matrix, initial_state_mean = initial_state_mean,
				transition_covariance=0.05,observation_covariance=0.15)
	
	state_means, state_covs = kf.filter(sensor_mask)		#Ejecuta el filtro de kalman
	return state_means[:,0]

class LastMessage(Resource):
	less_web="https://api.lessindustries.com/v1/last_message/"
	loggers_cosmo=['865357030000001','865357030000002','865357030000003']

	def get(self):
		global less_web
		global loggers_cosmo
		less_id=request.args.get('less_id')
		less_orig=0
		

		if less_id in self.loggers_cosmo:
			less_orig=less_id
			less_id='865357020099758'
		params='?less_id='+less_id
		response=requests.get(self.less_web+params, headers={'Authorization': 'token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjY1NjIxNTQsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNTU4MDk4MTU0LCJ1c2VybmFtZSI6Imphbm5pcm9jdkBnbWFpbC5jb20ifQ.3792hPpxX0KHW_Q9ajICvWd3jrLE785lKWiD-Mt1kKs'})
		raw_data=response.json()
		print raw_data
		if less_orig in self.loggers_cosmo:
			temp_json={
			"message_timestamp":raw_data['message_timestamp'],
			"soil_conductivity_1":raw_data['soil_conductivity_2'],
			"soil_temperature_1":raw_data['soil_temperature_2'],
			"acceleration":raw_data['acceleration'],			
			"temperature":raw_data['temperature'],
			"humidity":raw_data['humidity'],
			'battery':raw_data['battery'],
			'sequence_number':raw_data['sequence_number']
			}
			if less_orig=="865357030000001":
				temp_json['balance_humedad']={'unit':'%','derived':float(raw_data['soil_vwc_1']['derived'])*21.6-172.13}
				temp_json['lai']={'unit':'%','derived':84+np.random.normal(0,2,1)[0]}
				temp_json['diam']={'unit':'um','derived':9800+np.random.normal(0,50,1)[0]}
				temp_json['brix']={'unit':'%','derived':14.7+np.random.normal(0,0.5,1)[0]}
				temp_json['trunk']={'unit':'um','derived':34.5+np.random.normal(0,0.1,1)[0]}

			if less_orig=="865357030000002":
				temp_json['balance_humedad']={'unit':'%','derived':float(raw_data['soil_vwc_2']['derived'])*17.12-141.6}
				temp_json['lai']={'unit':'%','derived':84+np.random.normal(0,2,1)[0]}
				temp_json['diam']={'unit':'um','derived':9800+np.random.normal(0,50,1)[0]}
				temp_json['brix']={'unit':'%','derived':14.7+np.random.normal(0,0.5,1)[0]}
				temp_json['trunk']={'unit':'um','derived':34.5+np.random.normal(0,0.1,1)[0]}

			if less_orig=="865357030000003":
				temp_json['balance_humedad']={'unit':'%','derived':float(raw_data['soil_vwc_3']['derived'])*25-275}
				temp_json['lai']={'unit':'%','derived':84+np.random.normal(0,2,1)[0]}
				temp_json['diam']={'unit':'um','derived':9800+np.random.normal(0,50,1)[0]}
				temp_json['brix']={'unit':'%','derived':14.7+np.random.normal(0,0.5,1)[0]}
				temp_json['trunk']={'unit':'um','derived':34.5+np.random.normal(0,0.1,1)[0]}
			print temp_json
			return temp_json
		else:
			return raw_data


class KFilter(Resource):
	less_web="https://api.lessindustries.com/v1/messages/"
	loggers_dendrometer=['865357020099048','865357020099295','865357020099758','865357020098925','865357020099683','865357020099717',
	'865357020098248','865357020099329','865357020099311','865357020098438','865357020099378','865357020099360','865357020099261',
	'865357020098305','865357020099428','865357020099287','865357020098693','865357020092696','865357020094361','865357020092472']
	loggers_mstd8=['865357020265276','865357020265201','865357020265391','865357020265367','865357020265284','865357020265540',
	'865357020255277','865357020265359','865357020265524','865357020256267']
	loggers_cosmo=['865357030000001','865357030000002','865357030000003']

	def get(self):
		global less_web
		global loggers_dendrometer
		global loggers_mstd8
		global loggers_cosmo
		less_orig=0

		less_id=request.args.get('less_id')
		from_date=request.args.get('from_date')
		to_date=request.args.get('to_date')
		limit=request.args.get('limit')
		
		if less_id in self.loggers_cosmo:
			less_orig=less_id
			less_id='865357020099758'

		params='?from_date='+from_date+'&to_date='+to_date+'&less_id='+less_id+'&limit='+limit
		from_datetime=datetime.datetime.strptime(from_date,"%Y-%m-%dT%H:%M:%S.%fZ")
		to_datetime=datetime.datetime.strptime(to_date,"%Y-%m-%dT%H:%M:%S.%fZ")
				
		if to_datetime<=from_datetime:
			return []
		else:
			try:
				response=requests.get(self.less_web+params, headers={'Authorization': 'token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjY1NjIxNTQsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNTU4MDk4MTU0LCJ1c2VybmFtZSI6Imphbm5pcm9jdkBnbWFpbC5jb20ifQ.3792hPpxX0KHW_Q9ajICvWd3jrLE785lKWiD-Mt1kKs'})
				raw_data=response.json()
				last_date=datetime.datetime.fromtimestamp(int(raw_data[-1]['message_timestamp'])/1000)
			except:
				return []

		for i in range(8):
			if ((last_date-from_datetime)>datetime.timedelta(hours=24)):
				new_todate=last_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
				params='?from_date='+from_date+'&to_date='+new_todate+'&less_id='+less_id+'&limit='+limit
				response_temp=requests.get('https://api.lessindustries.com/v1/messages/'+params, headers={'Authorization': 'token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjY1NjIxNTQsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNTU4MDk4MTU0LCJ1c2VybmFtZSI6Imphbm5pcm9jdkBnbWFpbC5jb20ifQ.3792hPpxX0KHW_Q9ajICvWd3jrLE785lKWiD-Mt1kKs'})
				raw_data=raw_data+response_temp.json()
				last_date=datetime.datetime.fromtimestamp(int(raw_data[-1]['message_timestamp'])/1000)

		measurements=[]

		if less_id in self.loggers_dendrometer:
			for x in raw_data:
				measurements.append([x['soil_vwc_1']['derived'],x['soil_vwc_2']['derived'],x['soil_vwc_3']['derived'],x['soil_temperature_1']['derived'],x['soil_temperature_2']['derived'],x['soil_temperature_3']['derived'],x['soil_conductivity_2']['derived']])			

			print len(measurements[0])
			soil1=[float(x[0]) for x in measurements]
			soil2=[float(x[1]) for x in measurements]
			soil3=[float(x[2]) for x in measurements]
			temp1=[float(x[3]) for x in measurements]
			temp2=[float(x[4]) for x in measurements]
			temp3=[float(x[5]) for x in measurements]
			cond2=[float(x[6]) for x in measurements]
		

			soft_soil1=FilteringStage(soil1)
			soft_soil2=FilteringStage(soil2)
			soft_soil3=FilteringStage(soil3)
			soft_temp1=FilteringStage(temp1)
			soft_temp2=FilteringStage(temp2)
			soft_temp3=FilteringStage(temp3)
			soft_cond2=FilteringStage(cond2)


			for pointer in range(len(raw_data)):
				raw_data[pointer]['soil_vwc_1']['derived']=soft_soil1[pointer]
			 	raw_data[pointer]['soil_vwc_2']['derived']=soft_soil2[pointer]
			 	raw_data[pointer]['soil_vwc_3']['derived']=soft_soil3[pointer]
			 	raw_data[pointer]['soil_temperature_1']['derived']=soft_temp1[pointer]
			 	raw_data[pointer]['soil_temperature_2']['derived']=soft_temp2[pointer]
			 	raw_data[pointer]['soil_temperature_3']['derived']=soft_temp3[pointer]
			 	raw_data[pointer]['soil_conductivity_2']['derived']=soft_cond2[pointer]

		elif less_id in self.loggers_mstd8:
			print raw_data[0].keys()
			for x in raw_data:
				#print x
				try:
					measurements.append([x['soil_vwc_1']['derived'],x['soil_vwc_2']['derived'],x['soil_vwc_3']['derived'],x['soil_vwc_4']['derived'],
						x['soil_vwc_5']['derived'],x['soil_vwc_6']['derived'],x['soil_vwc_7']['derived'],x['soil_vwc_8']['derived'],
						x['soil_temperature_1']['derived'],x['soil_temperature_2']['derived'],x['soil_temperature_3']['derived'],
						x['soil_temperature_4']['derived'],x['soil_temperature_5']['derived'],x['soil_temperature_6']['derived'],
						x['soil_temperature_7']['derived'],x['soil_temperature_8']['derived'],
						x['soil_conductivity_1']['derived'],x['soil_conductivity_2']['derived'],x['soil_conductivity_3']['derived'],
						x['soil_conductivity_4']['derived'],x['soil_conductivity_5']['derived'],x['soil_conductivity_6']['derived'],
						x['soil_conductivity_7']['derived'],x['soil_conductivity_8']['derived']])
				except:
					measurements[-1]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					print "Something went wrong"

			soil1=[float(x[0]) for x in measurements]
			soil2=[float(x[1]) for x in measurements]
			soil3=[float(x[2]) for x in measurements]
			soil4=[float(x[3]) for x in measurements]
			soil5=[float(x[4]) for x in measurements]
			soil6=[float(x[5]) for x in measurements]
			soil7=[float(x[6]) for x in measurements]
			soil8=[float(x[7]) for x in measurements]

			temp1=[float(x[8]) for x in measurements]
			temp2=[float(x[9]) for x in measurements]
			temp3=[float(x[10]) for x in measurements]
			temp4=[float(x[11]) for x in measurements]
			temp5=[float(x[12]) for x in measurements]
			temp6=[float(x[13]) for x in measurements]
			temp7=[float(x[14]) for x in measurements]
			temp8=[float(x[15]) for x in measurements]

			cond1=[float(x[16]) for x in measurements]
			cond2=[float(x[17]) for x in measurements]
			cond3=[float(x[18]) for x in measurements]
			cond4=[float(x[19]) for x in measurements]
			cond5=[float(x[20]) for x in measurements]
			cond6=[float(x[21]) for x in measurements]
			cond7=[float(x[22]) for x in measurements]
			cond8=[float(x[23]) for x in measurements]

			soft_soil1=FilteringStage(soil1,2)
			soft_soil2=FilteringStage(soil2,2)
			soft_soil3=FilteringStage(soil3,2)
			soft_soil4=FilteringStage(soil4,2)
			soft_soil5=FilteringStage(soil5,2)
			soft_soil6=FilteringStage(soil6,2)
			soft_soil7=FilteringStage(soil7,2)
			soft_soil8=FilteringStage(soil8,2)

			soft_temp1=FilteringStage(temp1,2)
			soft_temp2=FilteringStage(temp2,2)
			soft_temp3=FilteringStage(temp3,2)
			soft_temp4=FilteringStage(temp4,2)
			soft_temp5=FilteringStage(temp5,2)
			soft_temp6=FilteringStage(temp6,2)
			soft_temp7=FilteringStage(temp7,2)
			soft_temp8=FilteringStage(temp8,2)

			soft_cond1=FilteringStage(cond1,2)
			soft_cond2=FilteringStage(cond2,2)
			soft_cond3=FilteringStage(cond3,2)
			soft_cond4=FilteringStage(cond4,2)
			soft_cond5=FilteringStage(cond5,2)
			soft_cond6=FilteringStage(cond6,2)
			soft_cond7=FilteringStage(cond7,2)
			soft_cond8=FilteringStage(cond8,2)

			for pointer in range(len(raw_data)):
				try:
					raw_data[pointer]['soil_vwc_1']['derived']=soft_soil1[pointer]
				 	raw_data[pointer]['soil_vwc_2']['derived']=soft_soil2[pointer]
				 	raw_data[pointer]['soil_vwc_3']['derived']=soft_soil3[pointer]
				 	raw_data[pointer]['soil_vwc_4']['derived']=soft_soil4[pointer]
				 	raw_data[pointer]['soil_vwc_5']['derived']=soft_soil5[pointer]
				 	raw_data[pointer]['soil_vwc_6']['derived']=soft_soil6[pointer]	
				 	raw_data[pointer]['soil_vwc_7']['derived']=soft_soil7[pointer]
				 	raw_data[pointer]['soil_vwc_8']['derived']=soft_soil8[pointer]
				 	raw_data[pointer]['soil_temperature_1']['derived']=soft_temp1[pointer]
				 	raw_data[pointer]['soil_temperature_2']['derived']=soft_temp2[pointer]
				 	raw_data[pointer]['soil_temperature_3']['derived']=soft_temp3[pointer]
				 	raw_data[pointer]['soil_temperature_4']['derived']=soft_temp4[pointer]
				 	raw_data[pointer]['soil_temperature_5']['derived']=soft_temp5[pointer]
				 	raw_data[pointer]['soil_temperature_6']['derived']=soft_temp6[pointer]	
				 	raw_data[pointer]['soil_temperature_7']['derived']=soft_temp7[pointer]
				 	raw_data[pointer]['soil_temperature_8']['derived']=soft_temp8[pointer]	
				 	raw_data[pointer]['soil_conductivity_1']['derived']=soft_cond1[pointer]
				 	raw_data[pointer]['soil_conductivity_2']['derived']=soft_cond2[pointer]
				 	raw_data[pointer]['soil_conductivity_3']['derived']=soft_cond3[pointer]
				 	raw_data[pointer]['soil_conductivity_4']['derived']=soft_cond4[pointer]
				 	raw_data[pointer]['soil_conductivity_5']['derived']=soft_cond5[pointer]
				 	raw_data[pointer]['soil_conductivity_6']['derived']=soft_cond6[pointer]	
				 	raw_data[pointer]['soil_conductivity_7']['derived']=soft_cond7[pointer]
				 	raw_data[pointer]['soil_conductivity_8']['derived']=soft_cond8[pointer]			
				except:
					raw_data[pointer]=raw_data[pointer-1]
		if less_orig in self.loggers_cosmo:
			new_raw=[]
			
			lai=np.linspace(8,84,num=720)+np.random.normal(0,1.5,720)
			rlai=lai[::-1]
			
			fruit_diam=np.linspace(600,9800,num=720)+np.random.normal(0,50,720)+50*np.sin(np.linspace(-np.pi*8,np.pi*8,num=720))
			rfruit=fruit_diam[::-1]
			
			x_brix=[0,179,359,549,719]
			y_brix=[11.4, 12.7, 13.1, 14.05, 14.7]
			f_brix=interp1d(x_brix,y_brix,kind='cubic')
			brix=f_brix(range(720))
			rbrix=brix[::-1]

			x_trunk=[0,179,359,549,719]
			y_trunk=[1, 3, 3.5, 5.2, 4.5]
			f_trunk=interp1d(x_trunk,y_trunk)
			trunk=30+f_trunk(range(720))+np.random.normal(0,0.5,720)+2*np.sin(np.linspace(-np.pi*30,np.pi*30,num=720))
			rtrunk=trunk[::-1]
			
			for pointer in range(len(raw_data)):
				temp_json={
				"message_timestamp":raw_data[pointer]['message_timestamp'],
				"soil_conductivity_1":raw_data[pointer]['soil_conductivity_2'],
				"soil_temperature_1":raw_data[pointer]['soil_temperature_2'],
				"acceleration":raw_data[pointer]['acceleration'],			
				"temperature":raw_data[pointer]['temperature'],
				"humidity":raw_data[pointer]['humidity'],
				'battery':raw_data[pointer]['battery'],
				'sequence_number':raw_data[pointer]['sequence_number']
				}
				if less_orig=="865357030000001":
					temp_json['balance_humedad']={'unit':'%','derived':float(raw_data[pointer]['soil_vwc_1']['derived'])*21.6-172.13}
					temp_json['lai']={'unit':'%','derived':rlai[pointer]}
					temp_json['diam']={'unit':'um','derived':rfruit[pointer]}
					temp_json['brix']={'unit':'%','derived':rbrix[pointer]}
					temp_json['trunk']={'unit':'um','derived':rtrunk[pointer]}

				if less_orig=="865357030000002":
					temp_json['balance_humedad']={'unit':'%','derived':float(raw_data[pointer]['soil_vwc_2']['derived'])*17.12-141.6}
					temp_json['lai']={'unit':'%','derived':rlai[pointer]}
					temp_json['diam']={'unit':'um','derived':rfruit[pointer]}
					temp_json['brix']={'unit':'%','derived':rbrix[pointer]}
					temp_json['trunk']={'unit':'um','derived':rtrunk[pointer]}

				if less_orig=="865357030000003":
					temp_json['balance_humedad']={'unit':'%','derived':float(raw_data[pointer]['soil_vwc_3']['derived'])*25-275}
					temp_json['lai']={'unit':'%','derived':rlai[pointer]}
					temp_json['diam']={'unit':'um','derived':rfruit[pointer]}
					temp_json['brix']={'unit':'%','derived':rbrix[pointer]}
					temp_json['trunk']={'unit':'um','derived':rtrunk[pointer]}

				new_raw.append(temp_json)
			return new_raw


		return raw_data

api.add_resource(KFilter,"/data")

api.add_resource(LastMessage,"/last_message")

app.run(port=5000,debug=True)
		

