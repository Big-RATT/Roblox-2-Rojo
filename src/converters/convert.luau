local fs = require("@lune/fs")
local roblox = require("@lune/roblox")
local serde = require("@lune/serde")
local process = require("@lune/process")

local args = process.args

if #args < 2 then
	print("Usage: lune run convert <input.rbxl|rbxm> <output_dir> [services_json]")
	process.exit(1)
end

local inputPath = args[1]:gsub("\\", "/")
local outputDir = args[2]:gsub("\\", "/")

local enabledServices = {}
if args[3] then
	local servicesJson = args[3]
	local decoded = serde.decode("json", servicesJson)
	for _, serviceName in decoded do
		enabledServices[serviceName] = true
	end
else
	enabledServices = {
		ServerScriptService = true,
		ReplicatedStorage = true,
		ServerStorage = true,
		StarterPlayer = true,
		StarterGui = true,
		ReplicatedFirst = true,
	}
end

local fileExtension = string.match(inputPath:lower(), "%.([^%.]+)$")
local isModel = fileExtension == "rbxm" or fileExtension == "rbxmx"

print("Loading", isModel and "RBXM" or "RBXL", "file:", inputPath)

local fileData = fs.readFile(inputPath)
local game

if isModel then
	local instances = roblox.deserializeModel(fileData)
	game = roblox.Instance.new("DataModel")
	for _, instance in instances do
		instance.Parent = game
	end
else
	game = roblox.deserializePlace(fileData)
end

print("✓ Loaded file")

if not fs.isDir(outputDir) then
	fs.writeDir(outputDir)
end

local srcDir = outputDir .. "/src"
if not fs.isDir(srcDir) then
	fs.writeDir(srcDir)
end

local inputFilename = inputPath:match("[^/\\]+$")
local outputFilename = string.gsub(string.gsub(inputFilename, "%.rbxl$", ".rbxlx"), "%.rbxm$", ".rbxmx")
local outputXmlPath = outputDir .. "/" .. outputFilename

local xmlData
if isModel then
	local instances = {}
	for _, child in game:GetChildren() do
		table.insert(instances, child)
	end
	xmlData = roblox.serializeModel(instances, true)
else
	xmlData = roblox.serializePlace(game, true)
end

fs.writeFile(outputXmlPath, xmlData)
print("✓ Saved XML file:", outputXmlPath)

local targetServices = {
	"ServerScriptService",
	"ReplicatedStorage",
	"ServerStorage",
	"StarterPlayer",
	"StarterGui",
	"ReplicatedFirst",
}

local scriptExtensions = {
	Script = "server.luau",
	LocalScript = "client.luau",
	ModuleScript = "luau",
}

local initScriptExtensions = {
	Script = "init.server.luau",
	LocalScript = "init.client.luau",
	ModuleScript = "init.luau",
}

local guiClasses = {
	ScreenGui = true,
	BillboardGui = true,
	SurfaceGui = true,
	Frame = true,
	ScrollingFrame = true,
	TextLabel = true,
	TextButton = true,
	TextBox = true,
	ImageLabel = true,
	ImageButton = true,
	ViewportFrame = true,
	CanvasGroup = true,
	UIListLayout = true,
	UIGridLayout = true,
	UIPadding = true,
	UICorner = true,
	UIStroke = true,
	UIGradient = true,
	UIAspectRatioConstraint = true,
	UISizeConstraint = true,
	UITextSizeConstraint = true,
}

local function sanitizeName(name)
	name = string.gsub(name, '[<>:"|?*]', '_')
	name = string.gsub(name, '[\\/]', '_')
	return name
end

local function serializeValue(value)
	local valueType = typeof(value)
	
	if valueType == "Color3" then
		return { Color3 = { value.R, value.G, value.B } }
	elseif valueType == "UDim2" then
		return {
			UDim2 = {
				{ value.X.Scale, value.X.Offset },
				{ value.Y.Scale, value.Y.Offset }
			}
		}
	elseif valueType == "UDim" then
		return { UDim = { value.Scale, value.Offset } }
	elseif valueType == "Vector2" then
		return { Vector2 = { value.X, value.Y } }
	elseif valueType == "Vector3" then
		return { Vector3 = { value.X, value.Y, value.Z } }
	elseif valueType == "CFrame" then
		local components = { value:GetComponents() }
		return { CFrame = components }
	elseif valueType == "Rect" then
		return nil
	elseif valueType == "Instance" then
		return nil
	elseif valueType == "EnumItem" then
		local enumString = tostring(value)
		local enumName = string.match(enumString, "[^%.]+$")
		return enumName or enumString
	elseif valueType == "Font" then
		return nil
	elseif valueType == "ColorSequence" or valueType == "NumberSequence" then
		return nil
	elseif valueType == "string" or valueType == "number" or valueType == "boolean" then
		return value
	else
		return nil
	end
end

local function serializeProperties(props)
	local serialized = {}
	for key, value in pairs(props) do
		local result = serializeValue(value)
		if result ~= nil then
			serialized[key] = result
		end
	end
	return serialized
end

local function getInstanceProperties(instance)
	local properties = {}
	local className = instance.ClassName
	
	local propertiesToExport = {
		"Visible", "ZIndex", "LayoutOrder",
		"ResetOnSpawn", "DisplayOrder", "ZIndexBehavior", "Enabled",
		"Size", "Position", "AnchorPoint", "Rotation",
		"BackgroundColor3", "BackgroundTransparency", "BorderColor3", "BorderSizePixel",
		"ClipsDescendants",
		"Text", "TextColor3", "TextSize", "TextScaled", "TextWrapped",
		"TextXAlignment", "TextYAlignment", "TextTransparency", "TextStrokeTransparency",
		"TextStrokeColor3",
		"Image", "ImageColor3", "ImageTransparency", "ImageRectOffset", "ImageRectSize",
		"ScaleType",
		"CanvasSize", "ScrollBarThickness",
		"AspectRatio",
		"CornerRadius",
		"Color", "Thickness", "Transparency", "ApplyStrokeMode",
		"PaddingLeft", "PaddingRight", "PaddingTop", "PaddingBottom",
		"CFrame",
	}
	
	for _, propName in propertiesToExport do
		local success, value = pcall(function()
			return instance[propName]
		end)
		
		if success and value ~= nil then
			properties[propName] = value
		end
	end
	
	return serializeProperties(properties)
end

local function ensureDir(path)
	if fs.isDir(path) then
		return
	end
	
	local parent = string.match(path, "(.+)/[^/]+$")
	if parent and not fs.isDir(parent) then
		ensureDir(parent)
	end
	
	local success, err = pcall(function()
		fs.writeDir(path)
	end)
	
	if not success then
		print("Warning: Failed to create directory:", path, err)
	end
end

local function processInstance(instance, parentPath)
	local className = instance.ClassName
	local name = sanitizeName(instance.Name)
	
	if className == "RemoteEvent" then
		local remotePath = parentPath .. "/" .. name
		ensureDir(remotePath)
		fs.writeFile(remotePath .. "/init.meta.json", serde.encode("json", {
			className = "RemoteEvent",
			ignoreUnknownInstances = true
		}, true))
		print("  • Created RemoteEvent:", name)
		return
	end
	
	if className == "RemoteFunction" then
		local remotePath = parentPath .. "/" .. name
		ensureDir(remotePath)
		fs.writeFile(remotePath .. "/init.meta.json", serde.encode("json", {
			className = "RemoteFunction",
			ignoreUnknownInstances = true
		}, true))
		print("  • Created RemoteFunction:", name)
		return
	end
	
	if className == "BindableEvent" then
		local remotePath = parentPath .. "/" .. name
		ensureDir(remotePath)
		fs.writeFile(remotePath .. "/init.meta.json", serde.encode("json", {
			className = "BindableEvent",
			ignoreUnknownInstances = true
		}, true))
		print("  • Created BindableEvent:", name)
		return
	end
	
	if className == "BindableFunction" then
		local remotePath = parentPath .. "/" .. name
		ensureDir(remotePath)
		fs.writeFile(remotePath .. "/init.meta.json", serde.encode("json", {
			className = "BindableFunction",
			ignoreUnknownInstances = true
		}, true))
		print("  • Created BindableFunction:", name)
		return
	end
	
	if className == "Animation" then
		local animPath = parentPath .. "/" .. name
		ensureDir(animPath)
		
		local meta = {
			className = "Animation",
			ignoreUnknownInstances = true
		}
		
		local successAnimId, animationId = pcall(function()
			return instance.AnimationId
		end)
		
		if successAnimId and animationId and animationId ~= "" then
			meta.properties = {
				AnimationId = animationId
			}
		end
		
		local success, err = pcall(function()
			fs.writeFile(animPath .. "/init.meta.json", serde.encode("json", meta, true))
		end)
		
		if success then
			print("  • Created Animation:", name)
		else
			print("  ✗ Failed to create Animation:", name, err)
		end
		
		return
	end
	
	local valueClasses = {
		CFrameValue = "CFrame",
		StringValue = "String",
		NumberValue = "Number",
		BoolValue = "Bool",
		IntValue = "Int",
		Vector3Value = "Vector3",
		ObjectValue = "Object",
		BrickColorValue = "BrickColor",
		Color3Value = "Color3",
	}
	
	local valueProp = valueClasses[className]
	if valueProp then
		local valuePath = parentPath .. "/" .. name
		ensureDir(valuePath)
		
		local meta = {
			className = className,
			ignoreUnknownInstances = true
		}
		
		local successValue, value = pcall(function()
			return instance.Value
		end)
		
		if successValue and value ~= nil then
			local serializedValue = serializeValue(value)
			if serializedValue ~= nil then
				meta.properties = {
					Value = serializedValue
				}
			end
		end
		
		local success, err = pcall(function()
			fs.writeFile(valuePath .. "/init.meta.json", serde.encode("json", meta, true))
		end)
		
		if success then
			print("  • Created " .. className .. ":", name)
		else
			print("  ✗ Failed to create " .. className .. ":", name, err)
		end
		
		return
	end
	
	if guiClasses[className] then
		local instancePath = parentPath .. "/" .. name
		ensureDir(instancePath)
		
		local meta = {
			className = className,
			ignoreUnknownInstances = true,
			properties = getInstanceProperties(instance)
		}
		
		local success, err = pcall(function()
			fs.writeFile(instancePath .. "/init.meta.json", serde.encode("json", meta, true))
		end)
		
		if success then
			print("  • Created GUI:", className, name)
		else
			print("  ✗ Failed to create GUI:", name, err)
		end
		
		for _, child in instance:GetChildren() do
			processInstance(child, instancePath)
		end
		
		return
	end
	
	if scriptExtensions[className] then
		local children = instance:GetChildren()
		local source = instance.Source or "-- Empty script\n"
		
		if #children > 0 then
			local scriptPath = parentPath .. "/" .. name
			ensureDir(scriptPath)
			
			local initFilename = initScriptExtensions[className]
			local success, err = pcall(function()
				fs.writeFile(scriptPath .. "/" .. initFilename, source)
			end)
			if success then
				print("  • Created script with children:", name .. "/" .. initFilename)
			else
				print("  ✗ Failed to create script:", name, err)
			end
			
			for _, child in children do
				processInstance(child, scriptPath)
			end
		else
			local extension = scriptExtensions[className]
			local scriptPath = parentPath .. "/" .. name .. "." .. extension
			local success, err = pcall(function()
				fs.writeFile(scriptPath, source)
			end)
			if success then
				print("  • Created script:", name .. "." .. extension)
			else
				print("  ✗ Failed to create script:", name, err)
			end
		end
		return
	end
	
	local children = instance:GetChildren()
	if #children > 0 then
		local instancePath = parentPath .. "/" .. name
		ensureDir(instancePath)
		
		local meta = {
			ignoreUnknownInstances = true
		}
		
		if className ~= "Folder" and className ~= "Model" then
			meta.className = className
		end
		
		local success, err = pcall(function()
			fs.writeFile(instancePath .. "/init.meta.json", serde.encode("json", meta, true))
		end)
		
		for _, child in children do
			processInstance(child, instancePath)
		end
	end
end

local projectTree = {
	name = "roblox-project",
	tree = {
		["$className"] = "DataModel"
	}
}

if isModel then
	print("Processing model instances...")
	projectTree.tree.Model = {
		["$path"] = "src/Model"
	}
	
	local modelDir = srcDir .. "/Model"
	ensureDir(modelDir)
	
	for _, instance in game:GetChildren() do
		processInstance(instance, modelDir)
	end
else
	for _, serviceName in targetServices do
		if not enabledServices[serviceName] then
			print("Skipping", serviceName, "(disabled in filter)")
			continue
		end
		
		local service = game:GetService(serviceName)
		
		if service then
			local serviceDir = srcDir .. "/" .. serviceName
			ensureDir(serviceDir)
			
			print("Processing " .. serviceName .. "...")
			
			if serviceName == "StarterPlayer" then
				projectTree.tree[serviceName] = {
					StarterPlayerScripts = {
						["$path"] = "src/StarterPlayer/StarterPlayerScripts"
					},
					StarterCharacterScripts = {
						["$path"] = "src/StarterPlayer/StarterCharacterScripts"
					}
				}
				
				for _, child in service:GetChildren() do
					if child.ClassName == "StarterPlayerScripts" or child.ClassName == "StarterCharacterScripts" then
						local subDir = serviceDir .. "/" .. child.Name
						ensureDir(subDir)
						
						for _, script in child:GetChildren() do
							processInstance(script, subDir)
						end
					end
				end
			else
				projectTree.tree[serviceName] = {
					["$path"] = "src/" .. serviceName
				}
				
				for _, child in service:GetChildren() do
					processInstance(child, serviceDir)
				end
			end
		end
	end
end

local projectPath = outputDir .. "/default.project.json"
fs.writeFile(projectPath, serde.encode("json", projectTree, true))
print("✓ Created default.project.json")

print("\n✓ Conversion completed successfully!")
print("Project created at:", outputDir)
