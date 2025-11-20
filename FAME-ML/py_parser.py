'''
Farzana Ahamed Bhuiyan (Lead) 
Akond Rahman 
Oct 20, 2020 
Parser needed to implement FAME-ML 
'''

import ast 
import os 
import constants 

"""
Added for SQA Project (Part 4.b):
- Integrated forensic logging
- logger imported below
- Two functions instrumented:
    * getPythonParseObject
    * getPythonAtrributeFuncs
"""

import logging
logger = logging.getLogger(__name__)

def checkLoggingPerData(tree_object, name2track):
    '''
    Check if data used in any load/write methods is logged ... called once for one load/write operation 
    '''
    LOGGING_EXISTS_FLAG = False 
    IMPORT_FLAG, FUNC_FLAG, ARG_FLAG  = False, False , False 
    for stmt_ in tree_object.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Import) :
                funcDict = node_.__dict__     
                # print(funcDict) 
                import_name_objects = funcDict[constants.NAMES_KW]
                for obj in import_name_objects:
                    if ( constants.LOGGING_KW in  obj.__dict__[constants.NAME_KW]): 
                        IMPORT_FLAG = True 
    func_decl_list = getPythonAtrributeFuncs(tree_object)
    for func_decl_ in func_decl_list:
        func_parent_id, func_name , funcLineNo, call_arg_list = func_decl_ # the class in which the method belongs, func_name, line no, arg_list 
        
        if ( constants.LOGGING_KW in func_parent_id ) or ( constants.LOGGING_KW in func_name) : 
            # print(func_parent_id, func_name, call_arg_list)  
            FUNC_FLAG = True 
            for arg_ in call_arg_list:
                if name2track in arg_:
                    ARG_FLAG = True 
    if (IMPORT_FLAG) and (FUNC_FLAG) and (ARG_FLAG):
        LOGGING_EXISTS_FLAG = True 
    return LOGGING_EXISTS_FLAG 


def func_def_log_check(func_decl_list):
    '''
    checks existence of logging in a list of function declarations ... useful for exception bodies 
    '''
    FUNC_FLAG = False 
    for func_decl_ in func_decl_list:
        func_parent_id, func_name , funcLineNo, call_arg_list = func_decl_ # the class in which the method belongs, func_name, line no, arg_list 
        if ( constants.LOGGING_KW in func_parent_id ) or ( constants.LOGGING_KW in func_name) : 
            # print(func_parent_id, func_name, call_arg_list)  
            FUNC_FLAG = True         
    return FUNC_FLAG 

def checkExceptLogging(except_func_list):
    return func_def_log_check( except_func_list ) 

    

def getPythonExcepts(pyTreeObj): 
    except_body_as_list = []
    for stmt_ in pyTreeObj.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.ExceptHandler): 
                exceptDict = node_.__dict__     
                except_body_as_list = exceptDict[constants.BODY_KW]  
    return except_body_as_list


def checkAttribFuncsInExcept(expr_obj):
    attrib_list = []
    for expr_ in expr_obj:
        expr_dict = expr_.__dict__
        if constants.VALUE_KW in expr_dict:
            func_node = expr_dict[constants.VALUE_KW] 
            if isinstance( func_node, ast.Call ):
                attrib_list = attrib_list + commonAttribCallBody( func_node )
    return attrib_list 

def getPythonParseObject(pyFile):
    """
    Modified for SQA Project (Part 4.b):
    - Added entry logging
    - Added file size logging
    - Added success logging
    - Added exception logging
    """
    logger.info(f"[getPythonParseObject] Attempting to parse: {pyFile}")

    try:
        content = open(pyFile).read()
        logger.debug(f"[getPythonParseObject] Loaded {len(content)} characters")

        full_tree = ast.parse(content)
        logger.info(f"[getPythonParseObject] Successfully parsed: {pyFile}")
        return full_tree

    except SyntaxError:
        logger.warning(f"[getPythonParseObject] SyntaxError while parsing: {pyFile}")
        return ast.parse(constants.EMPTY_STRING)

    except Exception as e:
        logger.exception(f"[getPythonParseObject] Unexpected failure on: {pyFile}")
        raise

def commonAttribCallBody(node_):
    full_list = []
    if isinstance(node_, ast.Call):
        funcDict = node_.__dict__ 
        func_, funcArgs, funcLineNo, funcKeys =  funcDict[ constants.FUNC_KW ], funcDict[constants.ARGS_KW], funcDict[constants.LINE_NO_KW], funcDict[constants.KEY_WORDS_KW]  
        if( isinstance(func_, ast.Attribute ) ):
            func_as_attrib_dict = func_.__dict__ 
            #print(func_as_attrib_dict ) 
            func_name    = func_as_attrib_dict[constants.ATTRIB_KW] 
            func_parent  = func_as_attrib_dict[constants.VALUE_KW]
            
            if( isinstance(func_parent, ast.Name ) ):     
                call_arg_list = []   
                index = 0                
                for x_ in range(len(funcArgs)):
                	index = x_ + 1
                	funcArg = funcArgs[x_] 
                	if( isinstance(funcArg, ast.Name ) )  :
                		call_arg_list.append( (  funcArg.id, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif( isinstance(funcArg, ast.Attribute) ): 
                		arg_dic  = funcArg.__dict__
                		arg_name = arg_dic[constants.ATTRIB_KW] 
                		call_arg_list.append( (  arg_name, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif(isinstance( funcArg, ast.Str ) ):
                	    call_arg_list.append( ( funcArg.s, constants.INDEX_KW + str( x_ + 1 )  ) )
                        
                for x_ in range(len(funcKeys)):
                	funcKey = funcKeys[x_] 
                	if( isinstance(funcKey, ast.keyword ) )  :
                		call_arg_list.append( ( funcKey.arg, constants.INDEX_KW + str( x_ + 1 + index ) ) ) 
                    			
                full_list.append( ( func_parent.id, func_name , funcLineNo, call_arg_list  ) )        
                
                
            if( isinstance(func_parent, ast.Attribute ) ):     
                call_arg_list = []   
                index = 0                
                for x_ in range(len(funcArgs)):
                	index = x_ + 1
                	funcArg = funcArgs[x_] 
                	if( isinstance(funcArg, ast.Name ) )  :
                	    call_arg_list.append( (  funcArg.id, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif( isinstance(funcArg, ast.Attribute) ): 
                	    arg_dic  = funcArg.__dict__
                	    arg_name = arg_dic[constants.ATTRIB_KW] 
                	    call_arg_list.append( (  arg_name, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif(isinstance( funcArg, ast.Str ) ):
                	    call_arg_list.append( ( funcArg.s, constants.INDEX_KW + str( x_ + 1 )  ) )
                        
                for x_ in range(len(funcKeys)):
                	funcKey = funcKeys[x_] 
                	if( isinstance(funcKey, ast.keyword ) )  :
                		call_arg_list.append( ( funcKey.arg, constants.INDEX_KW + str( x_ + 1 + index ) ) ) 
                		
                func_dic  = func_parent.__dict__
                func_parent_name = func_dic[constants.ATTRIB_KW] 
                full_list.append( ( func_parent_name, func_name , funcLineNo, call_arg_list  ) )    
                
            if( isinstance(func_parent, ast.Call ) ):     
                call_arg_list = []   
                index = 0                
                for x_ in range(len(funcArgs)):
                	index = x_ + 1
                	funcArg = funcArgs[x_] 
                	if( isinstance(funcArg, ast.Name ) )  :
                	    call_arg_list.append( (  funcArg.id, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif( isinstance(funcArg, ast.Attribute) ): 
                	    arg_dic  = funcArg.__dict__
                	    arg_name = arg_dic[constants.ATTRIB_KW] 
                	    call_arg_list.append( (  arg_name, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif(isinstance( funcArg, ast.Str ) ):
                		call_arg_list.append( ( funcArg.s, constants.INDEX_KW + str( x_ + 1 )  ) )
                        
                for x_ in range(len(funcKeys)):
                	funcKey = funcKeys[x_] 
                	if( isinstance(funcKey, ast.keyword ) )  :
                		call_arg_list.append( ( funcKey.arg, constants.INDEX_KW + str( x_ + 1 + index ) ) ) 
                		
                func_dic  = func_parent.__dict__
                func_parent_name = func_dic[constants.FUNC_KW] 
                if( isinstance(func_parent_name, ast.Name ) ):  
                	full_list.append( ( func_parent_name.id, func_name , funcLineNo, call_arg_list  ) )      
    return full_list             


"""
UPDATED: getPythonAtrributeFuncs (Part 4.b Logging Integration)
"""
def getPythonAtrributeFuncs(pyTree):
    """
    Modified for SQA Project (Part 4.b):
    - Added entry logging
    - Added count of functions found
    - Added detailed debug logging for each detected attribute call
    """
    logger.info("[getPythonAtrributeFuncs] Extracting attribute-style function calls")

    attrib_call_list = []
    try:
        for stmt_ in pyTree.body:
            for node_ in ast.walk(stmt_):
                if isinstance(node_, ast.Call):
                    # Extract call details using existing logic
                    extracted = commonAttribCallBody(node_)
                    attrib_call_list += extracted

                    if extracted:
                        logger.debug(f"[getPythonAtrributeFuncs] Detected: {extracted}")

        logger.info(f"[getPythonAtrributeFuncs] Total calls extracted: {len(attrib_call_list)}")
        return attrib_call_list

    except Exception:
        logger.exception("[getPythonAtrributeFuncs] Failed during AST traversal")
        raise
    
def getFunctionAssignments(pyTree):
    """
    Extract function calls that appear on the right-hand side of assignments.
    Updated for Part 4B to be more defensive against malformed AST nodes.
    """
    call_list = []

    for stmt_ in getattr(pyTree, "body", []):
        # Defensive handling: skips nodes that cannot be walked
        try:
            walker = ast.walk(stmt_)
        except Exception:
            continue

        for node_ in walker:
            if not isinstance(node_, ast.Assign):
                continue

            lhs = ""
            assign_dict = getattr(node_, "__dict__", {})

            # Extracts assignment components safely
            targets = assign_dict.get(constants.TARGETS_KW, [])
            value = assign_dict.get(constants.VALUE_KW, None)

            # We only analyze calls on RHS
            if not isinstance(value, ast.Call):
                continue

            funcDict = getattr(value, "__dict__", {})
            funcName = funcDict.get(constants.FUNC_KW, None)
            funcArgs = funcDict.get(constants.ARGS_KW, [])
            funcLineNo = funcDict.get(constants.LINE_NO_KW, -1)
            funcKeys = funcDict.get(constants.KEY_WORDS_KW, [])

            # Safely extracts LHS name
            for target in targets:
                if isinstance(target, ast.Name):
                    lhs = target.id

            # Defensive check: funcName must exist
            if funcName is None:
                continue

            # Case 1: funcName is a direct identifier (e.g., foo(x))
            if isinstance(funcName, ast.Name):
                call_arg_list = []
                idx_offset = 0

                # Extracts positional arguments
                for i, funcArg in enumerate(funcArgs):
                    idx_offset = i + 1
                    try:
                        if isinstance(funcArg, ast.Name):
                            call_arg_list.append((funcArg.id, constants.FUNC_CALL_ARG_STR + str(idx_offset)))
                        elif isinstance(funcArg, ast.Str):
                            call_arg_list.append((funcArg.s, constants.FUNC_CALL_ARG_STR + str(idx_offset)))
                    except Exception:
                        # Skips malformed args
                        continue

                # Extracts keyword arguments
                for j, funcKey in enumerate(funcKeys):
                    if isinstance(funcKey, ast.keyword):
                        call_arg_list.append(
                            (funcKey.arg, constants.FUNC_CALL_ARG_STR + str(j + 1 + idx_offset))
                        )

                call_list.append((lhs, funcName.id, funcLineNo, call_arg_list))

            # Case 2: funcName is an attribute (e.g., module.foo(x))
            elif isinstance(funcName, ast.Attribute):
                call_arg_list = []
                idx_offset = 0
                func_name_dict = getattr(funcName, "__dict__", {})
                func_name = func_name_dict.get(constants.ATTRIB_KW, None)

                # Defensive: skips malformed attribute names
                if func_name is None:
                    continue

                for i, funcArg in enumerate(funcArgs):
                    idx_offset = i + 1
                    try:
                        if isinstance(funcArg, ast.Call):
                            func_arg_dict = funcArg.__dict__
                            func_arg = func_arg_dict.get(constants.FUNC_KW, None)
                            call_arg_list.append((func_arg, constants.FUNC_CALL_ARG_STR + str(idx_offset)))

                        elif isinstance(funcArg, ast.Attribute):
                            func_arg_dic = funcArg.__dict__
                            func_arg = func_arg_dic.get(constants.ATTRIB_KW, None)
                            call_arg_list.append((func_arg, constants.FUNC_CALL_ARG_STR + str(idx_offset)))

                        elif isinstance(funcArg, ast.Str):
                            call_arg_list.append((funcArg.s, constants.FUNC_CALL_ARG_STR + str(idx_offset)))

                        elif isinstance(funcArg, ast.Subscript):
                            # Extracts subscript base
                            base = funcArg.value
                            if isinstance(base, ast.Name):
                                call_arg_list.append((base.id, constants.FUNC_CALL_ARG_STR + str(idx_offset)))
                    except Exception:
                        continue

                # Extracts keyword args
                for j, funcKey in enumerate(funcKeys):
                    if isinstance(funcKey, ast.keyword):
                        call_arg_list.append(
                            (funcKey.arg, constants.FUNC_CALL_ARG_STR + str(j + 1 + idx_offset))
                        )

                call_list.append((lhs, func_name, funcLineNo, call_arg_list))

    return call_list
    
    
def getFunctionDefinitions(pyTree):
    """
    Extract standalone function calls (not assignments).
    Updated for Part 4B to be more defensive against malformed AST nodes
    and unexpected types produced by fuzzing.
    """
    func_list = []

    # Walks only valid top-level statements
    for stmt_ in getattr(pyTree, "body", []):
        try:
            walker = ast.walk(stmt_)
        except Exception:
            continue

        for node_ in walker:
            # Only analyzes call expressions
            if not isinstance(node_, ast.Call):
                continue

            funcDict = getattr(node_, "__dict__", {})

            func_ = funcDict.get(constants.FUNC_KW, None)
            funcArgs = funcDict.get(constants.ARGS_KW, [])
            funcLineNo = funcDict.get(constants.LINE_NO_KW, -1)
            funcKeys = funcDict.get(constants.KEY_WORDS_KW, [])

            if func_ is None:
                continue

            # Case 1: Simple call like foo(x)
            if isinstance(func_, ast.Name):
                func_name = func_.id
                call_arg_list = []
                idx_offset = 0

                # Positional args
                for i, arg in enumerate(funcArgs):
                    idx_offset = i + 1
                    try:
                        if isinstance(arg, ast.Name):
                            call_arg_list.append((arg.id, constants.INDEX_KW + str(idx_offset)))
                        elif isinstance(arg, ast.Attribute):
                            arg_dic = arg.__dict__
                            call_arg_list.append((arg_dic.get(constants.ATTRIB_KW), constants.INDEX_KW + str(idx_offset)))
                        elif isinstance(arg, ast.Call):
                            inner = arg.__dict__.get(constants.FUNC_KW, None)
                            call_arg_list.append((inner, constants.INDEX_KW + str(idx_offset)))
                        elif isinstance(arg, ast.Str):
                            call_arg_list.append((arg.s, constants.INDEX_KW + str(idx_offset)))
                    except Exception:
                        continue

                # Keyword args
                for j, funcKey in enumerate(funcKeys):
                    if isinstance(funcKey, ast.keyword):
                        call_arg_list.append((funcKey.arg, constants.INDEX_KW + str(j + idx_offset + 1)))

                func_list.append((func_name, funcLineNo, call_arg_list))

            # Case 2: Attribute call like module.foo(x)
            elif isinstance(func_, ast.Attribute):
                func_name_dict = getattr(func_, "__dict__", {})
                func_name = func_name_dict.get(constants.ATTRIB_KW, None)
                if func_name is None:
                    continue

                call_arg_list = []
                idx_offset = 0

                for i, arg in enumerate(funcArgs):
                    idx_offset = i + 1
                    try:
                        if isinstance(arg, ast.Name):
                            call_arg_list.append((arg.id, constants.INDEX_KW + str(idx_offset)))
                        elif isinstance(arg, ast.Attribute):
                            arg_dic = arg.__dict__
                            call_arg_list.append((arg_dic.get(constants.ATTRIB_KW), constants.INDEX_KW + str(idx_offset)))
                        elif isinstance(arg, ast.Call):
                            inner = arg.__dict__.get(constants.FUNC_KW, None)
                            call_arg_list.append((inner, constants.INDEX_KW + str(idx_offset)))
                        elif isinstance(arg, ast.Str):
                            call_arg_list.append((arg.s, constants.INDEX_KW + str(idx_offset)))
                    except Exception:
                        continue

                for j, funcKey in enumerate(funcKeys):
                    if isinstance(funcKey, ast.keyword):
                        call_arg_list.append((funcKey.arg, constants.INDEX_KW + str(j + idx_offset + 1)))

                func_list.append((func_name, funcLineNo, call_arg_list))

    return func_list


    
    
def getFunctionAssignmentsWithMultipleLHS(pyTree):
    call_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
            	lhs = []
            	assign_dict = node_.__dict__
            	targets, value  =  assign_dict[  constants.TARGETS_KW ], assign_dict[  constants.VALUE_KW ]
            	if isinstance(value, ast.Call):
                    funcDict = value.__dict__ 
                    funcName, funcArgs, funcLineNo =  funcDict[ constants.FUNC_KW ], funcDict[ constants.ARGS_KW ], funcDict[constants.LINE_NO_KW] 
                    for target in targets:
                    	if( isinstance(target, ast.Name) ):
                            lhs.append(target.id) 
                    	elif( isinstance(target, ast.Tuple) ):
                    		for item in target.elts:
                    			if isinstance(item, ast.Name):
                    				lhs.append(item.id)
                    if( isinstance(funcName, ast.Name ) ): 
                    	call_arg_list = []       
                    	for x_ in range(len(funcArgs)):
                    		funcArg = funcArgs[x_] 
                    		if( isinstance(funcArg, ast.Name ) ):
                    			call_arg_list.append( ( funcArg.id, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )             
                    		elif( isinstance( funcArg, ast.Str ) ):
                    			call_arg_list.append( ( funcArg.s, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance( funcArg, ast.Call ) ):
                    			func_arg_dict  = funcArg.__dict__
                    			func_arg = func_arg_dict[constants.FUNC_KW] 
                    			call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance( funcArg, ast.Attribute ) ): 
                    			func_arg_dic  = funcArg.__dict__
                    			func_arg = func_arg_dic[constants.ATTRIB_KW] 
                    			call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) ) 
                    	call_list.append( ( lhs, funcName.id, funcLineNo, call_arg_list )  )	
                    elif( isinstance( funcName, ast.Attribute ) ):
                    	call_arg_list = []       
                    	func_name_dict  = funcName.__dict__
                    	func_name = func_name_dict[constants.ATTRIB_KW] 
                    	for x_ in range(len(funcArgs)):
                    		funcArg = funcArgs[x_] 
                    		if( isinstance(funcArg, ast.Name ) ):
                        		call_arg_list.append( ( funcArg.id, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif(isinstance( funcArg, ast.Str ) ):
                        		call_arg_list.append( ( funcArg.s, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance( funcArg, ast.Call ) ):
                        		func_arg_dict  = funcArg.__dict__
                        		func_arg = func_arg_dict[constants.FUNC_KW] 
                        		call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance(funcArg, ast.Attribute) ): 
                    			func_arg_dic  = funcArg.__dict__
                    			func_arg = func_arg_dic[constants.ATTRIB_KW] 
                    			call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) )   ) 
                    	call_list.append( ( lhs, func_name, funcLineNo, call_arg_list )  )

    return call_list 
    

def getModelFeature(pyTree):
    feature_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
            	lhs = ''
            	assign_dict = node_.__dict__
            	targets, value  =  assign_dict[  constants.TARGETS_KW ], assign_dict[  constants.VALUE_KW ]
            	if isinstance(value, ast.Attribute):
                    funcDict = value.__dict__ 
                    className, featureName, funcLineNo =  funcDict[ constants.VALUE_KW ], funcDict[ constants.ATTRIB_KW ], funcDict[ constants.LINE_NO_KW ] 
                    for target in targets:
                    	if( isinstance(target, ast.Name) ):
                            lhs = target.id 
                    if( isinstance(className, ast.Name ) ): 
                    	feature_list.append( ( lhs, className.id, featureName, funcLineNo)  )	
            	if isinstance(value, ast.Subscript):
                	value =  value.value
                	if isinstance(value, ast.Attribute):
                		funcDict = value.__dict__ 
                		className, featureName, funcLineNo =  funcDict[ constants.VALUE_KW ], funcDict[ constants.ATTRIB_KW ], funcDict[constants.LINE_NO_KW] 
                		for target in targets:
                			if( isinstance(target, ast.Name) ):
                				lhs = target.id 
                		if( isinstance(className, ast.Name ) ): 
                			feature_list.append( ( lhs, className.id, featureName, funcLineNo)  )
                		elif( isinstance(className, ast.Attribute ) ): 
                			class_dic  = className.__dict__
                			class_name = class_dic[constants.ATTRIB_KW] 
                			feature_list.append( ( lhs, class_name, featureName, funcLineNo)  )	

    return feature_list 
    
    
def getTupAssiDetails(pyTree): 
    var_assignment_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
            	lhs = ''
            	assign_dict = node_.__dict__
            	targets, value  =  assign_dict[ constants.TARGETS_KW ], assign_dict[  constants.VALUE_KW ]
            	if isinstance(value, ast.ListComp):
                    varDict = value.__dict__ 
                    varName, varValue, varLineNo =  varDict[ constants.ELT_KW ], varDict[ constants.GENERATORS_KW ], varDict[ constants.LINE_NO_KW ] 
                    for target in targets:
                    	if( isinstance(target, ast.Name) ):
                            lhs = target.id 
                    if isinstance(varName, ast.Subscript):
                    	varName =  varName.value
                    	if isinstance(varName, ast.Name):
                    		varName = varName.id
                    if isinstance(varValue, list):
                    	varValue =  varValue[0]
                    	if isinstance(varValue, ast.comprehension):
                    		varIter = varValue.iter
                    		if isinstance(varIter, ast.Name):
                    			varIter = varIter.id
                    		varValue = varValue.target
                    		if isinstance(varValue, ast.Name):
                    			varValue = varValue.id
                    var_assignment_list.append( (lhs, varName, varValue, varIter, varLineNo) )

    return var_assignment_list     
    
    
def getImport(pyTree): 
    import_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
        	if isinstance(node_, ast.Import):
        		for name in node_.names:
        			import_list.append( (name.name.split('.')[0] ) )
        	elif isinstance(node_, ast.ImportFrom):
        		if(node_.module is not None):
        			import_list.append( ( node_.module.split('.')[0] ) )

    return import_list 

def checkIfParsablePython( pyFile ):
	flag = True 
	try:
		full_tree = ast.parse( open( pyFile ).read())    
	except (SyntaxError, UnicodeDecodeError) as err_ :
		flag = False 
	return flag 	