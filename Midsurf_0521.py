import ansa
import sfunc2
from ansa import base
from ansa import constants
from ansa import connections
import math
import collections
from collections import Counter
from ansa import mesh

#	Midsurf
# ====================================================================================
# create set
def CreateSet(name,opt=0):
	vals = {'Name': name}
	nset = base.CreateEntity(constants.ANSYS, "SET", vals)
	n = 1
	while not nset:
		nset = base.CreateEntity(constants.ANSYS, 'SET', {'Name': name +'_' + str(n)})
		n += 1
	if opt == 0:
		return nset._id
	else:
		return nset
# ====================================================================================
def AutoFixGeometry(part):
	options = ["OVERLAPS","TRIPLE CONS","CRACKS","NEEDLE FACES","UNCHECKED FACES","COLLAPSED CONS","SINGLE CONS"]
	fix = [1, 1, 1, 1, 1, 1, 1]
	ret = base.CheckAndFixGeometry(part, options, fix, True, True)
	return ret
# ====================================================================================
def CalcAreaSum(facelist):
	area_sum = 0
	for face in facelist:
		area = base.GetFaceArea(face)
		area_sum += area
	return area_sum
# ====================================================================================
def GetMaxFace(facelist):
	area_max = 0
	for face in facelist:
		area = base.GetFaceArea(face)
		if area > area_max:
			area_max = area
			face_id = face._id
	face_max = base.GetEntity(constants.ANSYS, 'FACE', face_id )
	return face_max
# ====================================================================================
def MidsurfCheck():
	faces1 = base.CollectEntities(constants.ANSYS, None,'FACE',filter_visible=True)
	props1 = base.CollectEntities(constants.ANSYS, None,'PSHELL',filter_visible=True)
	if len(faces1) == 0:
		sfunc2.Log("Midsurf","MidsurfCheck : No faces found !","warnning")
		pass
	else :
		# get one of the faces
		face_id1 = faces1[0]._id
		face_1= base.GetEntity(ansa.constants.ANSYS, "FACE", face_id1)
		# set only selected face to be visible
		status = base.Or(face_1)
		base.Neighb("ALL")
		faces2 = base.CollectEntities(constants.ANSYS, None,'FACE',filter_visible=True)
		# estimate whether the surface is continuous
		if len(faces2) < len(faces1) :
			return 0
		else:
			return 1
# ====================================================================================
def AutoSking(part, thickness):
	volumes = base.CollectEntities(constants.ANSYS, part, 'VOLUME',recursive=True)
	if len(volumes) == 0:
		pass
	else:
		base.DeleteEntity(volumes)
	options = ["OVERLAPS","TRIPLE CONS","CRACKS","NEEDLE FACES","UNCHECKED FACES","COLLAPSED CONS","SINGLE CONS"]
	fix = [1, 1, 1, 1, 1, 1, 1]
	ret = base.CheckAndFixGeometry(part, options, fix, True, True)
	#ret = base.AutoFixGeometry(part)
	if ret != None:
		sfunc2.Log("Midsurf","Erro occured in PART:{0}".format(part._name),"err")
		sfunc2.Log("Midsurf","Error occured in PART:{0}".format(part._name),"err","Midsurf_Ansa.err")
	else:
		base.Or(part)
		base.SetViewAngles(f_key="F10")
		all_faces = base.CollectEntities(constants.ANSYS, part, "FACE",recursive=True)
		t_temp = thickness * 1.2
		make_skin = base.Skin(apply_thickness=True, new_pid=False, offset_type=2, ok_to_offset=True, max_thickness=t_temp, delete=False, entities=all_faces)
		if make_skin != 0:
			status = base.Not(all_faces)
			ret = MidsurfCheck()
			if ret ==1:
				base.DeleteEntity(all_faces)
				sfunc2.Log("Midsurf","Make skin successfully for PART:{0}".format(part._name),"info")
				base.All()
				return part
			else:
				sfunc2.Log("Midsurf",'Midsurface is discontinuous ! part name : {0}!'.format(str(part._name)),"warnning")
				base.All()
		else:
			sfunc2.Log("Midsurf","Make skin unsuccessfully for PART:{0}".format(part._name),"err")
			sfunc2.Log("Midsurf","Make skin unsuccessfully for PART:{0}".format(part._name),"err","Midsurf_Ansa.err")
			base.All()
			a = 10/0
# ====================================================================================
def OffSet(part, thickness):
	volumes = base.CollectEntities(constants.ANSYS, part, 'VOLUME',recursive=True)
	if len(volumes) == 0:
		volu = float('inf')
	else:
		volu = base.CalcSolidVolume(volumes[0])
		base.DeleteEntity(volumes)
	options = ["OVERLAPS","TRIPLE CONS","CRACKS","NEEDLE FACES","UNCHECKED FACES","COLLAPSED CONS","SINGLE CONS"]
	fix = [1, 1, 1, 1, 1, 1, 1]
	ret = base.CheckAndFixGeometry(part, options, fix, True, True)
	if ret != None:
		sfunc2.Log("Midsurf","Erro occured in PART:{0}".format(part._name),"err")
		sfunc2.Log("Midsurf","Error occured in PART:{0}".format(part._name),"err","Midsurf_Ansa.err")
	else:
		base.Or(part)
		round_faces = []
		all_conss = base.CollectEntities(constants.ANSYS, part, "CONS",recursive=True)
		all_faces = base.CollectEntities(constants.ANSYS, part, "FACE",recursive=True)
		area_sum = CalcAreaSum(all_faces)
		face_max = GetMaxFace(all_faces)
		face_list1 = base.GatherFaces(face_max, feature_angle=89, visibility='visible')
		area_master = CalcAreaSum(face_list1)
		for cons in all_conss:
			vals = ('Length',)
			length = base.GetEntityCardValues(entity=cons, fields=vals, deck=constants.ANSYS)
			#print(length)
			if length['Length'] > (thickness-0.001) and  (length['Length'] < thickness+0.001):
				#print('hh')
				faces = base.GetFacesOfCons(cons)
				round_faces.extend(faces)
		round_faces = list(set(round_faces).difference(set(face_list1)))
		conss_r = base.CollectEntities(constants.ANSYS, round_faces, "CONS",recursive=True)
		base.ReleaseCons(conss_r)
		ms_faces = list(set(all_faces)-set(round_faces))
		face_o = ms_faces[0]
		master_faces = base.GatherFaces(face_o, feature_angle=179, visibility='visible')
		slave_faces = list(set(ms_faces)-set(master_faces))
		if len(slave_faces) > len(master_faces):
			faces_list2 = slave_faces
			face_k = master_faces[0]
			len_k = len(master_faces)
		else:
			faces_list2 = master_faces
			face_k = slave_faces[0]
			len_k = len(slave_faces)
		faces_k = base.GatherFaces(face_k, feature_angle=179, visibility='visible')
		if area_master*thickness/volu > 0.94 or area_master/area_sum >0.45:
			offsetFaces = base.OffsetFaces(thickness/(-2), "KEEP", faces_list1)
		elif len(faces_k) == len_k:
			offsetFaces = base.OffsetFaces(thickness/(-2), "KEEP", faces_list2)
		else:
			sfunc2.Log("Midsurf","Offset faces unsuccessfully for PART:{0}".format(part._name),"err")
			sfunc2.Log("Midsurf","Offset faces unsuccessfully for PART:{0}".format(part._name),"err","Midsurf_Ansa.err")
			base.All()
			a = 10/0
		if offsetFaces == 0:
			props = base.CollectEntities(constants.ABAQUS, master_faces, "SHELL_SECTION", prop_from_entities=True)
			vals_t = {"T":thickness,}
			for prop in props:
				base.SetEntityCardValues(constants.ABAQUS, prop,vals_t)
			base.DeleteFaces(all_faces)
			base.All()
			sfunc2.Log("Midsurf","Offset faces successfully for PART:{0}".format(part._name),"info")
			return part
		else:
			sfunc2.Log("Midsurf","Offset faces unsuccessfully for PART:{0}".format(part._name),"err")
			sfunc2.Log("Midsurf","Offset faces unsuccessfully for PART:{0}".format(part._name),"err","Midsurf_Ansa.err")
			base.All()
			a = 10/0
# ====================================================================================
def AutoCasting(part, thickness):
	volumes = base.CollectEntities(constants.ANSYS, part, 'VOLUME',recursive=True)
	if len(volumes) == 0:
		pass
	else:
		base.DeleteEntity(volumes)
	options = ["OVERLAPS","TRIPLE CONS","CRACKS","NEEDLE FACES","UNCHECKED FACES","COLLAPSED CONS","SINGLE CONS"]
	fix = [1, 1, 1, 1, 1, 1, 1]
	ret = base.CheckAndFixGeometry(part, options, fix, True, True)
	#ret = base.AutoFixGeometry(part)
	if ret != None:
		sfunc2.Log("Midsurf","Erro occured in PART:{0}".format(part._name),"err")
		sfunc2.Log("Midsurf","Error occured in PART:{0}".format(part._name),"err","Midsurf_Ansa.err")
	else:
		base.Or(part)
		base.SetViewAngles(f_key="F10")
		all_faces = base.CollectEntities(constants.ANSYS, part, "FACE")
		ret = base.MidSurfAuto(thick=thickness/2, faces=all_faces, handle_as_single_solid=False, length=thickness*3, elem_type=3, paste_triple_len=50,paste_triple_len_as_percentage=True,part="use_current",property="use_current")
		if ret == 0:
			shells = base.CollectEntities(constants.ANSYS, None, "SHELL", filter_visible = True)
			props_orig = base.CollectEntities(constants.ABAQUS, all_faces, "SHELL_SECTION", prop_from_entities=True)
			props_new = base.CollectEntities(constants.ABAQUS, shells, "SHELL_SECTION", prop_from_entities=True)
			base.SetEntityPart(shells, part)
			vals_t = {"T":thickness,}
			for prop in props_new:
				base.SetEntityCardValues(constants.ABAQUS, prop,vals_t)
			base.DeleteFaces(all_faces)
			base.DeleteEntity(props_orig)
			base.All()
			sfunc2.Log("Midsurf","Auto casting successfully for PART:{0}".format(part._name))
			return shells
		else:
			sfunc2.Log("Midsurf","Auto casting unsuccessfully for PART:{0}".format(part._name),"err")
			sfunc2.Log("Midsurf","Auto casting unsuccessfully for PART:{0}".format(part._name),"err","Midsurf_Ansa.err")
# ====================================================================================
def Midsurf(dic_bom_file):
	skin_done = CreateSet('skin done',1)
	casting_done = CreateSet('casting done',1)
	list_done = []
	shell_casting = []
	dic_shell_thickness = dic_bom_file["dic_shell_thickness"]
	dic_mesh_type = dic_bom_file["dic_mesh_type"]
	list_org_comp = dic_bom_file["list_org_comp"]
	deck = base.CurrentDeck()
	for comp in list_org_comp:
		if dic_mesh_type[comp]=="shell":
			ents = base.NameToEnts(comp, deck,match = constants.ENM_EXACT)
			for ent in ents:
				if ent._ansaType(deck) == "ANSAPART":
					thickness = dic_shell_thickness[comp]
					try:
						part = AutoSking(ent, thickness)
						if part != None:
							list_done.append(part)
					except:
						try:
							part = OffSet(part, thickness)
							if part != None:
								list_done.append(part)
						except:
							shells = AutoCasting(ent, thickness)
							if shells!= None:
								list_done.append(ent)
								shell_casting.append(shells)
	base.AddToSet(skin_done, list_done)
	base.AddToSet(casting_done, shell_casting)
	sfunc2.Log("Midsurf","Midsurf Finished !")
	return shell_casting
