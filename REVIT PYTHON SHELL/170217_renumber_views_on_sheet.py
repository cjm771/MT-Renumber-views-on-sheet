# these commands get executed in the current scope
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.UI import TaskDialog
import clr

import operator
#<--- LOG IMPORTS -->
import traceback
import time,datetime,os
import inspect
#<--- END LOG IMPORTS -->
import math
import json
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
from Autodesk.Revit.DB import * 

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
SHEET = doc.ActiveView

#constants
RAW_WRITE = True 

# <------------ LOG STUFF -------------------->#
#dependencies
#import traceback
#import time,datetime, os
#import inspect

#constants
LOGFILE =  "T:\Malcolm-Chris\REVIT\PYTHON REVIT SHELL\log.txt"
LOG_ACTIVE = False	

def log(textArr,is_raw=False):
    global LOGFILE,LOG_ACTIVE
    if LOG_ACTIVE:
        activeScript = os.path.basename(__file__)
        #---- prefix to identify time and script running ---#
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        current_line_no = inspect.stack()[1][2]
        current_function_name = inspect.stack()[1][3]
        precursor = "["+activeScript+":"+current_function_name+":"+str(current_line_no)+" // "+timestamp+"] --> "
        #---- end prefix --->
        filename =  LOGFILE
        if not isinstance(textArr, (list, tuple)):
            textArr = [textArr]
        target = open(filename, 'a+')
        target.write("\n")
        target.write(precursor)
        for i in textArr:
            if (not is_raw):
                target.write(repr(i))
            else:
                target.write(i)
        target.close()

def clearLog():
    global LOGFILE,LOG_ACTIVE
    if LOG_ACTIVE:
        filename =  LOGFILE
        target = open(filename, 'w+')
        target.write("")
        target.close()
        
# <------------ LOG STUFF -------------------->#

def is_array(var):
    return isinstance(var, (list, tuple))


def transpose(lis):
	return map(list, zip(*lis))

def dicViewer(dic):
	list = []
	for key,val in dic.items():
		list.append(["key:"+str(key),val])
	return list

def getPtList(dic):
	list = []
	for key,val in dic.items():
		list.append(map(lambda x: float(x), key.split(",")))
	return list


def seq(start, stop, step=1):
    n = int(round((stop - start)/float(step)))
    if n > 1:
        return([start + step*i for i in range(n+1)])
    else:
        return([])


def listToDic(list):
	dic = {}
	for i in list:
		i[0] = i[0].replace("key:","")
		dic[i[0]] = i[1]
	return dic

def xyToPoint(xyPt):
	return [xyPt[0],xyPt[1],0]
	#return Point.ByCoordinates(xyPt[0],xyPt[1],0)
	
def getClosest(x,n):
	return 	math.floor(x / n) * n;

#closestNode finds what the closest node pt is based on distance 
def closestNode(pt,nodes,stepX,stepY,allPts=False):
    """Return closest point to coord from points"""
    #move from bottom right point to top left point for the noses:)
    #nodesData = {orig: nodes, topLeft: map(lambda x: [x[0]+stepX,x[1]+stepY], nodes)}
    nodesData = map(lambda x: {"orig": x, "topLeft": [x[0]+stepX,x[1]+stepY]}, nodes)
    #measure dists
    dists = [(math.sqrt(pow(pt[0] -  nodeData['topLeft'][0], 2) + pow(pt[1] - nodeData['topLeft'][1], 2)), nodeData['orig']) for nodeData in  nodesData]  
    dists = sorted(dists, key=lambda x: x[0])
    # list of (dist, point) tuples
    nearest = min(dists)
    if allPts:
        return dists
    else:
        return nearest[1]  # return point only

#closestNode2 finds what cell it is in
def closestNode2(coord, points,stepX,stepY):
    currIndex = 0
    for index, bottomRightNodePt in enumerate(points):
        #we get the offset of the node cell to get top left and we already have bottom right\
        topLeftNodePt= [bottomRightNodePt[0]+stepX,bottomRightNodePt[1]+stepY]
        #now well test if our test pt is in x coord range and y coord range
        if (inRange(coord[0], topLeftNodePt[0], bottomRightNodePt[0]) and
            inRange(coord[1], topLeftNodePt[1], bottomRightNodePt[1])):
                currIndex = index
    #return the defualt
    return points[currIndex]

def inRange(testNum, rangeNum1, rangeNum2):
    if rangeNum1>rangeNum2:
        start = rangeNum2
        end = rangeNum1
    else:
        start = rangeNum1
        end = rangeNum2
    return (start<=testNum and testNum<=end)
    

def getNewDetailViewNumber(pts,offsetX, offsetY, stepX, stepY,gridPtsDic):
	newPts = []
	notClosestPts = []
	newPtsPts = [] 
	detailViewNumber = []
	if not is_array(pts[0]):
	    pts = [pts]
	for pt in pts:
		approxPt = ([round(getClosest(pt[0], stepX)+offsetX,2),round(getClosest(pt[1], stepY)+offsetY,2)])
		log(["approxPt",approxPt])
		closestPt = closestNode2(pt, getPtList(gridPtsDic),stepX,stepY)
		newPtsPts.append(xyToPoint(closestPt))
		newPts.append(closestPt)
		detailViewNumber.append(gridPtsDic[",".join(map(lambda x: str(x), closestPt))])
	#Assign your output to the OUT variable.
	return {
	"closestNodePt": closestPt,
	"detailViewNumber":detailViewNumber,
	"notClosestPts":notClosestPts, 
	"newPtsPts":newPtsPts
	}

#ensure the bounds are always top left to bottom right
def fixBoundsLine(MIN, MAX):
    firstPt = XYZ(min(MIN.X,MAX.X), max(MIN.Y,MAX.Y),0)
    secondPt = XYZ(max(MIN.X,MAX.X), min(MIN.Y,MAX.Y),0)
    return (firstPt,secondPt)


def getDataFromTitleBlock():
	global SHEET
	titleBlocksOnSheet = []
	fec = FilteredElementCollector(doc).OwnedByView(SHEET.Id)
	log(["fec: ",fec])
	for el in fec:
		if (el.Category!=None and "title blocks" in el.Category.Name.lower()):
			titleBlocksOnSheet.append(el)
	log(["titleblocks on sheet:", titleBlocksOnSheet])
	retData = {
		"detailGrid_bounds": None,
		"detailGrid_matrix": None,
		"detailGrid_endPts": None
	}
	for tb in titleBlocksOnSheet:
		#see if we can get bounds
		bb = tb.get_BoundingBox(SHEET)
		log(["titleblock_bounds:",bb])
		log(["title block_bounds min:",bb.Min, "max:",bb.Max])

		if retData['detailGrid_bounds']==None:
			 retData['detailGrid_bounds'] = getParam(tb, "detailGrid_bounds")
		if retData['detailGrid_matrix']==None:
			 retData['detailGrid_matrix'] = getParam(tb, "detailGrid_matrix")
			 
	#parse bouunds 
	boundOffsets = None
	if retData['detailGrid_bounds'] != None:
		if json is not None:
			try:
				boundsOffsets = json.loads(retData['detailGrid_bounds'])
				log(["json data from bounds:",boundsOffsets])
			except:
				log(["error when parsing detailGrid_bounds from titleblock..invalid json?"])
		else:
			boundsOffsets = parseBoundsWithoutJSON(retData['detailGrid_bounds'])
		

		if boundsOffsets is not None:
				retData["detailGrid_endPts"] = [ [bb.Min.X+boundsOffsets[0][0],bb.Max.Y-boundsOffsets[0][1],0],[bb.Max.X-boundsOffsets[1][0],bb.Min.Y+boundsOffsets[1][1],0]]

	#parse matrix
	if retData['detailGrid_matrix'] !=None:
		if json is not None:
			try:
				retData['detailGrid_matrix'] = json.loads(retData['detailGrid_matrix'])
			except:
				log(["error when parsing detailGrid_matrix from titleblock..invalid json?",e])
		else:
			retData['detailGrid_matrix'] = parseMatrixWithoutJSON(retData['detailGrid_matrix'])				


	log(["detailGrid data found from title block:",retData])
	return retData


def listToXYZPt(_list):
	return XYZ(_list[0],_list[1], _list[2])

def getPtGrid():
	
	#first lets see if the data for the bounds is in the titleblock
	titleBlockData = getDataFromTitleBlock()

	#<-------bounds---------->
	#embedded in titleblock?
	if (titleBlockData["detailGrid_endPts"]!=None):
		startPt = listToXYZPt(titleBlockData["detailGrid_endPts"][0])
		endPt = listToXYZPt(titleBlockData["detailGrid_endPts"][1])
	else:
		#else we can ask for user to select diagonal bounds line
		bbCrvRef = pickObject()
		bbCrv = elementFromReference(bbCrvRef).GeometryCurve
		#fix the diagonal line
		endPts = fixBoundsLine(bbCrv.GetEndPoint(0),bbCrv.GetEndPoint(1))
		startPt = endPts[0]
		endPt =  endPts[1]

		log("drawnLineCrv:",[startPt,endPt])
	
	
	#<-------grid---------->
	#embedded in titleblock?
	if (titleBlockData["detailGrid_matrix"]!=None):
		detailGrid = titleBlockData["detailGrid_matrix"]
	else:
	# else, manual grid thing...CHANGE THIS IF GRID IS DIFFERENT! 
		detailGrid = [
			["30" ,"25" ,"20" ,"15" ,"10","05"],
			["29" ,"24" ,"19" ,"14" ,"09","04"],
			["28" ,"23" ,"18" ,"13" ,"08" ,"03"],
			["27" ,"22" ,"17" ,"12" ,"07" ,"02"],
			["26" ,"21" ,"16" ,"11" ,"06" ,"01"]]
	

	xDiv = len(detailGrid[0])
	yDiv = len(detailGrid)

	detailGridFlat = reduce(operator.add, transpose(detailGrid))
	count = 0 
	stepX = round((endPt.X-startPt.X)/(xDiv),2)
	stepY = round((endPt.Y-startPt.Y)/(yDiv),2)
	for i in seq(startPt.X, endPt.X-stepX, stepX):
		for j in seq(startPt.Y, endPt.Y-stepY,  stepY):
			coords[str(round(i,2))+","+str(round(j,2))]= detailGridFlat[count]
			count=count+1

	#Assign your output to the OUT variable.
	return { "coords": coords,
		"offsetX": startPt.X,
		"offsetY": endPt.Y,
		"stepX": stepX,
		"stepY": stepY
		}
	

def getDetailNumFromPt(pt,gridPtsDic):
    return gridPtsDic[",".join(map(lambda x: str(x), pt))]

def removeDuplicate(num,pt,numsList,gridPtsDic):
    global stepX,stepY
    newDetailNum = False
    if num in numsList:
    	log(["getPtList:",getPtList(gridPtsDic)])
        closestNums = closestNode(pt, getPtList(gridPtsDic), stepX,stepY,True)
        for i,node in enumerate(closestNums):
            #item 0: distance, item 1: pt
            nodeDist = node[0]
            nodePt = node[1]
            log(["nodePt:",nodePt,"gridPtsDic:",gridPtsDic])
            detailNum = getDetailNumFromPt(nodePt,gridPtsDic)
            if detailNum not in numsList:
                newDetailNum = detailNum
                break
        if newDetailNum==False:
            #we didnt find any close ones, start going up from leng
            newDetailNum = len(gridPtsDic)+1
            while newDetailNum in numsList and newDetailNum<1000:
                newDetailNum=newDetailNum+1
        return newDetailNum
    else:
        return num


def elementFromId(id):
	log(["id:", id])
	global doc
	return doc.GetElement(id)


def setBuiltInParam(el, builtInParamEnum, value):
	global doc
	param = getBuiltInParam(el, builtInParamEnum, True)
	if not param.IsReadOnly:
		param.Set(value)
		doc.Regenerate()
	else:
		log(["Coult not edit ",paramName," on ",el, ". It is read only parameter // Read Only: ",param.IsReadOnly])


def setParam(el, paramName, value):
	global doc
	param = getParam(el, paramName, True)
	if not param.IsReadOnly:
		param.Set(value)
		#doc.Regenerate()
	else:
		log(["Coult not edit ",paramName," on ",el, ". It is read only parameter // Read Only: ",param.IsReadOnly])

def getBuiltInParam(el, builtInParamEnum, asParamObject=False):
	param = el.Parameter[builtInParamEnum]
	if not asParamObject:
		param = param.AsString()
	return param

def getParam(el, paramName, asParamObject=False):
	params = getParameters(el, asParamObject)
	if paramName in params:
		return params[paramName]
	else:
		return None

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def getParameters(el,asParamObject=False):
	global doc
	parameters = el.Parameters
	#log(["parameters for ",el,":",parameters])
	params = {}
	for param in parameters:
		if (asParamObject==False):
			params[param.Definition.Name] = param.AsString()
		else:
			params[param.Definition.Name] = param
	#get type params as well	
	#log(["parameters for ",el,":",params])
	#log(["typeid: ",el.GetTypeId()])
	isValidTypeId = True if (el.GetTypeId().IntegerValue > 0) else False
	#log(["invalid type element id? ",el,":",isValidTypeId])
	typeParams = {}
	if isValidTypeId:
		typeElement = doc.GetElement(el.GetTypeId())
		#log(["typeElement for ",el,":",typeElement])
		typeParams = getParameters(typeElement, asParamObject)
	return merge_two_dicts(params,typeParams)

def elementFromReference(ref):
	global doc
	id = ref.ElementId
	return doc.GetElement(id)


def createDetailLine(pt1, pt2):
	if  isinstance(pt1, (list, tuple)):
		pt1 = XYZ(pt1[0],pt1[1],pt1[2])
	if  isinstance(pt2, (list, tuple)):
		pt2 = XYZ(pt2[0],pt2[1],pt2[2])
	global app, SHEET
	startPoint =  XYZ( pt1.X, pt1.Y, 0);
	endPoint = 	  XYZ( pt2.X, pt2.Y, 0 );
	geomLine = Line.CreateBound(startPoint, endPoint)
	log(["line pts: ", startPoint, endPoint])
	log(["geomLine: ", geomLine])
	doc.Create.NewDetailCurve(SHEET, geomLine)

def getPointsFromViewports(viewport):
	try:
		outline = viewport.GetLabelOutline()
	except:
		outline = viewport.GetBoxOutline()
		
	PT = [outline.MaximumPoint.X,outline.MinimumPoint.Y,0]	
	#createDetailLine(outline.MaximumPoint, outline.MinimumPoint)
	return PT
	
def highlightDuplicates(pts):
	if (len(pts)>0):
		TaskDialog.Show ("Views share same cell", "Success! But "+str(len(pts))+" view(s) shared the same cell, they have been highlighted with a line for you to double check.")
		for pt in pts:
			createDetailLine(pt, [pt[0]+100,pt[1]+100,0])

def pickObject():
    
    __window__.Hide()
    TaskDialog.Show ("Select Bounds Line", "Select the diagonal line representing the grid bounds after closing this dialog.")
    picked = uidoc.Selection.PickObject(ObjectType.Element)
    #__window__.Topmost = True
    #__window__.Show()
    return picked

 

# clear log file
clearLog()

 #<------------- the stuff ------------>
#lets get the guide curve
try:
	t = Transaction(doc, 'Rename Detail Numbers')
	t.Start()

	log(["app",app])
	coords = {}
	ptGridData = getPtGrid()

	stepX = ptGridData['stepX']
	stepY = ptGridData['stepY']
	viewports = map(lambda x: elementFromId(x), SHEET.GetAllViewports())
	titleBlockPts = map(lambda x: getPointsFromViewports(x) ,viewports)
	log(titleBlockPts)
	detailViewNumberData = getNewDetailViewNumber(titleBlockPts,ptGridData['offsetX'], ptGridData['offsetY'],ptGridData['stepX'], ptGridData['stepY'],ptGridData['coords'])



	log(["detailViewNumberdata:",detailViewNumberData]) 
	#<----- handle duplicate detail numbers ---->
	detailNums = detailViewNumberData['detailViewNumber']
	duplicateList = []
	for i,detailNum in enumerate(detailNums):
	    if (detailNums.index(detailNum)!=i):
	        duplicateList.append(titleBlockPts[i])
	        detailNums[i] = removeDuplicate(detailNum,titleBlockPts[i],detailNums,ptGridData['coords'])
	detailViewNumberData['detailViewNumber'] = detailNums
	#<---- end handle duplicate detail numbers--->

	log(["DetailViewNumberData:",detailViewNumberData])

	paramEnum = BuiltInParameter.VIEWPORT_DETAIL_NUMBER

	# <---- Make unique numbers	
	for i, viewport in enumerate(viewports):
		currentVal = getBuiltInParam(viewport, paramEnum)
		setBuiltInParam(viewport, paramEnum, currentVal+"x")	

	for i, viewport in enumerate(viewports):
		log("current view Number: "+ str(detailViewNumberData["detailViewNumber"][i]))
		setBuiltInParam(viewport, paramEnum,str(detailViewNumberData["detailViewNumber"][i]))

	# <--- give duplicate warning, (views were found in same cell)
	highlightDuplicates(duplicateList)
	t.Commit()


except SyntaxError, e:
	log(["Error!\n---------\n", traceback.format_exc()],RAW_WRITE)

except Exception, e:
	log(["Error!\n---------\n", traceback.format_exc()],RAW_WRITE)

 #<------------- end of the stuff ------------>



__window__.Close()