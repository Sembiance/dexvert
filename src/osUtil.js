import {xu, fg} from "xu";
import {path} from "std";
import {RUNTIME} from "./Program.js";
import {appendCommonFuncs} from "./autoItUtil.js";
import {C} from "./C.js";

export async function run({f, cmd, osid="win2k", args=[], cwd, meta, script, scriptPre, timeout=xu.MINUTE*10, dontMaximize, quoteArgs, noAuxFiles, alsoKill=[], xlog})
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

	if(osid.startsWith("win"))
	{
		appendCommonFuncs(scriptLines, {script, scriptPre, timeout, alsoKill, fullCmd});

		scriptLines.push(`$osProgramPID = Run${script ? "" : (timeout ? "WaitWithTimeout" : "Wait")}('${binAndArgs}', '${cwd || "c:\\in"}'${dontMaximize ? "" : ", @SW_MAXIMIZE"}${script || !timeout ? "" : `, ${timeout}`})`);
		if(script)
			scriptLines.push(script);
	}

	osData.script = scriptLines.join("\n");

	xlog.info`Running OS ${fg.peach(osid)} ${fg.orange(cmd)} ${args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}`;
	xlog.debug`osData: ${osData}`;
	xlog.debug`\tSCRIPT: ${osData.script}`;
	const r = await (await fetch(`http://${C.OS_SERVER_HOST}:${C.OS_SERVER_PORT}/osRun`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(osData)})).text();
	if(r!=="ok")
		throw new Error(r);
		
	return r;
}
