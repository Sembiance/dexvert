import {xu, fg} from "xu";
import {fileUtil} from "xutil";
import {path, delay, assertStrictEquals} from "std";
import {Program} from "../../src/Program.js";
import {XLog} from "xlog";
import {DEV_MACHINE} from "../dexUtil.js";

const programs = {};
export {programs};

let initCalled = false;

export const programDirPath = path.join(import.meta.dirname, "..", "..", "src", "program");

async function loadProgramFilePath(programFilePath, {reload}={})
{
	if(programFilePath.endsWith("programs.js"))
		return;

	const programModule = await import(reload ? `${programFilePath}#${Date.now() + performance.now()}` : programFilePath);
	const programid = Object.keys(programModule).find(k => k.at(0)!=="_");

	// class name must match filename
	assertStrictEquals(programid, path.basename(programFilePath, ".js"), `program file [${programFilePath}] does not have a matching class name [${programid}]`);

	// check for duplicates
	if(!reload && programs[programid])
		throw new Error(`program [${programid}] at ${programFilePath} is a duplicate of ${programs[programid]}`);

	// create the class and validate it
	programs[programid] = programModule[programid].create();
	if(!(programs[programid] instanceof Program))
		throw new Error(`program [${programid}] at [${programFilePath}] is not of type Program`);
	
	if(programs[programid].allowDupOut && !programs[programid].chain && !["binsciiPrepare", "callFunction", "dirOpener", "strings", "unHexACX"].includes(programid))
		console.warn(`program ${programid} has ${"allowDupOut"} set to true, but does not have a ${"chain"} this is quite dangerous! Could lead to infinite recursion on processing server`);
}

export async function init(xlog=new XLog(DEV_MACHINE ? "info" : "error"))
{
	if(initCalled)
		return;
	initCalled = true;

	const programFilePaths = await fileUtil.tree(programDirPath, {nodir : true, regex : /[^/]+\/.+\.js$/});
	xlog.info`Loading ${programFilePaths.length} program files...`;
	await Promise.all(programFilePaths.map(loadProgramFilePath));
	xlog.debug`Loaded ${Object.keys(programs).length} programs`;
}

export async function programChanged({type, filePath}, xlog=new XLog("info"))
{
	if(!filePath || filePath.endsWith("programs.js"))
		return;
	
	if(type==="create" || type==="modify")
	{
		try
		{
			await delay(250);	// give the file time to finish writing, most important for newly created files
			await loadProgramFilePath(filePath, {reload : true});
			xlog.info`${fg.violet("RELOADED")} program/${path.relative(programDirPath, filePath)}`;
		}
		catch(err) { xlog.error`FAILED to RELOAD program: ${filePath} error: ${err}`; }
	}
	else if(type==="delete")
	{
		delete programs[path.basename(filePath, ".js")];
		xlog.info`${fg.violet("UNLOADED")} program/${path.relative(programDirPath, filePath)}`;
	}
}
