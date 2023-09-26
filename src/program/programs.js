import {xu} from "xu";
import {fileUtil} from "xutil";
import {path, assertStrictEquals} from "std";
import {Program} from "../../src/Program.js";
import {XLog} from "xlog";

const programs = {};
export {programs};

let hasInitialized = false;

export async function init(xlog=new XLog("error"))
{
	if(hasInitialized)
		return;

	const programDirPath = path.join(xu.dirname(import.meta), "..", "..", "src", "program");
	xlog.info`Finding program JS files...`;
	const programFilePaths = await fileUtil.tree(programDirPath, {nodir : true, regex : /[^/]+\/.+\.js$/});
	xlog.info`Processing ${programFilePaths.length} program files...`;

	for(const programFilePath of programFilePaths)
	{
		const programModule = await import(programFilePath);
		const programid = Object.keys(programModule)[0];

		// class name must match filename
		assertStrictEquals(programid, path.basename(programFilePath, ".js"), `program file [${programFilePath}] does not have a matching class name [${programid}]`);

		// check for duplicates
		if(programs[programid])
			throw new Error(`program [${programid}] at ${programFilePath} is a duplicate of ${programs[programid]}`);

		// create the class and validate it
		try
		{
			programs[programid] = programModule[programid].create();
		}
		catch(err)
		{
			xlog.error`Error creating program [${programid}] at [${programFilePath}]`;
			console.log(err, programModule[programid]);
		}
		if(!(programs[programid] instanceof Program))
			throw new Error(`program [${programid}] at [${programFilePath}] is not of type Program`);
		
		if(programs[programid].allowDupOut && !programs[programid].chain && !["unHexACX"].includes(programid))
			xlog.warn`program ${programid} has ${"allowDupOut"} set to true, but does not have a ${"chain"} this is quite dangerous! Could lead to infinite recursion on processing server`;
	}

	hasInitialized = true;
}
