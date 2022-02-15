import os
from string import ascii_uppercase as ABC

module_names = []
limit = 100
for c1 in ABC:
    for c2 in ABC:
        if limit <= 0:
            break
        limit -= 1
        module_name = c1 + c2
        module_names.append(module_name)
        source_dir = os.path.join("Sources", module_name)

        # 1. Create stub source folder
        os.makedirs(source_dir, exist_ok=True)
        source_content ="""
public struct %s {
    public init() {
    }
}
""" % (module_name)
        source_name = module_name + ".swift"

        # 2. Create stub source files
        with open(os.path.join(source_dir, source_name), "w") as f:
            f.write(source_content)

# 3. Generate client source code
source_code = ""
for module_name in module_names:
    source_code += "import %s\n" % (module_name)
source_code += "\n"
source_code += "public func testStubFrameworks() {\n"
for module_name in module_names:
    source_code += "    let _ = %s()\n" % (module_name)
source_code += "}"
with open("StubFrameworks.swift", "w") as source_f:
    source_f.write(source_code)

# 4. SwiftPM generate Xcodeproj
xcodeproj_path = "StubFrameworks.xcodeproj"
if not os.path.exists(xcodeproj_path):
    os.system("swift package generate-xcodeproj")

# 5. Create xcconfig, setting to static framework and long search path
xcconfig_path = "StubFrameworks.xcconfig"
with open(xcconfig_path, "w") as f:
    framework_search_paths = list(map(lambda x : "/path/not/found/%s" % (x), module_names))
    f.write("MACH_O_TYPE = staticlib\n")
    f.write("EXCLUDED_ARCHS = arm64 i386\n") # I'm not testing M1 Mac :)
    f.write("FRAMEWORK_SEARCH_PATHS = ")
    for module_name in module_names:
        for i in range(10):
            f.write("/path/not/found/%s/%d " % (module_name, i))

# 6. Xcodebuild build framework
sdk = "iphonesimulator"
configuration = "Debug"
cmd = "xcodebuild build -project %s -xcconfig %s -configuration %s -sdk %s " % (xcodeproj_path, xcconfig_path, configuration, sdk)
for module_name in module_names:
    cmd += " -target %s" % (module_name)
print(cmd)
os.system(cmd)
