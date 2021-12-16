

import sfunc4
import json, os, math, inspect, sys,re
import ansa
from ansa import base
from ansa import utils
from ansa import constants gfff


# ====================================================================================
def AutoAssignMaterial(path_mat,name_ptm):
	deck = base.CurrentDeck()
	print (path_mat)
	base.ReadMaterialDatabase(deck, path_mat)
	base.CopyMatsFromMdbToMlist(deck, "copy", False, True, True, False)
	parts = base.CollectEntities(deck,None,'ANSAPART')
	matlist = base.CollectEntities(deck,None,"__MATERIALS__")
	for part in parts:
		matname = name_ptm[part._name]
		mats = base.NameToEnts(matname,deck,constants.ENM_EXACT)
		if mats == None:
			sfunc4.Log("MatDefine","Material {1} was not found in material database for part :{0} !".format(part._name, matname),"err")
			sfunc4.Log("MatDefine","Please Check material database or input dict !")
			sfunc4.Log("MatDefine","Material {1} was not found in material database for part :{0} !".format(part._name, matname),"err","MatDefine_Ansa.err")
			val_mid = 1000000
		else:
			for mat in mats:
				if mat in matlist:
					val_mid =  mat._id
		if deck == constants.PAMCRASH:
			mat_label = 'IMAT'
		else:
			mat_label = 'MID'
		vals = {'Name': part._name, mat_label: val_mid}
		props = base.CollectEntities(deck, part,"__PROPERTIES__", prop_from_entities = True)
		for prop in props:
			base.SetEntityCardValues(deck, prop, vals)
	sfunc4.Log("MatDefine","Auto assign material finished !")
# ====================================================================================
def	MatDefine(dic_bom_file):
	#	�������cad�����в�����������Ͽ�������Ƶ�ӳ���ϵ �ֵ�matname_map kΪcad�в������� vΪ���Ͽ��в�������
	#	��bom��Ϣ�л�ȡ �������б�
	# list_all_mat ���������еĲ�������
	list_all_mat = dic_bom_file["list_all_mat"]
	#	ÿ�������Ӧ�Ĳ��ϣ�k�������v������
	dic_mat = dic_bom_file["dic_mat"]
	
	matname_map = sfunc4.ReadDicFromJsonFile("matname_map.json")
	
	list_matname_map = []
	for k,v in matname_map.items():
		list_matname_map.append(k)
	for matname in list_all_mat:
		if matname in list_matname_map:
			pass
		else:
			sfunc4.Log("MatDefine","{0} was not in material mapping list !".format(matname),"err")
			sfunc4.Log("MatDefine","{0} was not in material mapping list !".format(matname),"err","MatDefine_Ansa.err")
			return
	dic = {}
	for k,v in dic_mat.items():
		dic[k] = matname_map[v]
	
	current_path = inspect.getfile(inspect.currentframe())  
	dir_name = os.path.dirname(current_path)
	path_mat = os.path.abspath(dir_name) 
		

	AutoAssignMaterial(path_mat,dic)  	# pathΪ���ϴ洢·��������ʵ��Ӧ����������Ƿ���Ҫ�޸�  
	sfunc4.Log("MatDefine","Auto assign material finished !") 
	return True