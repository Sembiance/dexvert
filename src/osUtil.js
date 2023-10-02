import {xu, fg} from "xu";
import {path} from "std";
import {RUNTIME} from "./Program.js";
import {appendCommonFuncs} from "./autoItUtil.js";

export const OS_SERVER_HOST = "127.0.0.1";
export const OS_SERVER_PORT = 17735;
export const OSIDS = ["win2k", "winxp", "amiga"];

export async function run({f, cmd, osid="win2k", args=[], cwd, meta, script, scriptPre, timeout=xu.MINUTE*5, dontMaximize, quoteArgs, noAuxFiles, alsoKill=[], xlog})
{
	let fullCmd = cmd;
	const osData = {osid, cmd, meta, timeout, outDirPath : f.outDir.absolute};

	if(RUNTIME.globalFlags.osPriority)
		osData.osPriority = true;
	
	const inFiles = [f.input];
	if(!noAuxFiles)
		inFiles.push(...(f.files.aux || []));
	const inFilesRel = inFiles.map(v => v.rel);
	osData.inFilePaths = inFiles.map(v => v.absolute);

	const scriptLines = [];
	let binAndArgs = "";
	if(osid.startsWith("win"))
	{
		fullCmd = (/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`;
		binAndArgs += `"${fullCmd}"`;

		const q = quoteArgs ? '"' : "";
		if(args.length>0)
			binAndArgs += ` ${args.map(v => (inFilesRel.includes(v) ? `c:\\in\\${path.basename(v)}` : v)).map(v => `${q}${v.split("").map(c => ([" ", "'"].includes(c) ? `' & "${c}" & '` : (c==='"' ? `' & '"' & '` : c))).join("")}${q}`).join(" ")}`;
	}
	else if(osid.startsWith("amiga"))
	{
		binAndArgs += cmd;
		if(args.length>0)
			binAndArgs += ` ${args.map(arg => (inFilesRel.includes(arg) ? (path.basename(arg).includes(" ") ? `"HD:in/${path.basename(arg)}"` : `HD:in/${path.basename(arg)}`) : (arg.includes(" ") && !arg.includes('"') ? `"${arg}"` : arg))).join(" ")}`;
	}

	if(osid.startsWith("win"))
	{
		appendCommonFuncs(scriptLines, {script, scriptPre, timeout, alsoKill, fullCmd});

		scriptLines.push(`$osProgramPID = Run${script ? "" : (timeout ? "WaitWithTimeout" : "Wait")}('${binAndArgs}', '${cwd || "c:\\in"}'${dontMaximize ? "" : ", @SW_MAXIMIZE"}${script || !timeout ? "" : `, ${timeout}`})`);
		if(script)
			scriptLines.push(script);
	}
	else if(osid.startsWith("amiga"))
	{
		// Build an Amiga script
		scriptLines.push("/* dexvert go script */");	// A comment on the first line is REQUIRED for a script to be runnable!
		if(script)
			scriptLines.push(...Array.force(script));
		else
			scriptLines.push(`ADDRESS command ${binAndArgs.includes(`"`) ? `'` : `"`}${binAndArgs}${binAndArgs.includes(`"`) ? `'` : `"`}`);
		
		scriptLines.push("EXIT");
	}

	osData.script = scriptLines.join("\n");

	xlog.info`Running OS ${fg.peach(osid)} ${fg.orange(cmd)} ${args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}`;
	xlog.debug`osData: ${osData}`;
	xlog.debug`\tSCRIPT: ${osData.script}`;
	const r = await (await fetch(`http://${OS_SERVER_HOST}:${OS_SERVER_PORT}/osRun`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(osData)})).text();
	if(r!=="ok")
		throw new Error(r);
		
	return r;
}
