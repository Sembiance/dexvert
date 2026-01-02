import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil, hashUtil} from "xutil";
import {path} from "std";

export class diskExpressSFX extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	unsafe  = true;
	loc     = "msdos";
	pre     = async r =>
	{
		const {size, bytes} = (await Program.runProgram(`diskExpressInfo[outDirname:${r.f.outDir.base}]`, r.f.input, {xlog : r.xlog, autoUnlink : true})).meta || {};
		if(!size || !bytes)
		{
			r.xlog.warn`Failed to determine disk size from diskExpressInfo program.`;
		}
		else
		{
			r.floppyType = {"160K" : "360k", "180K" : "360k", "320K" : "360k", "360K" : "360k", "720K" : "720k", "1.2M" : "1.2m", "1.44M" : "1.44m", "2.88M" : "2.88m"}[size];
			r.floppyFilePath = path.join(r.cwd, "floppy.img");
			await runUtil.run("mkfs.fat", ["-F", "12", "-C", r.floppyFilePath, bytes/1024], {xlog : r.xlog});
			r.floppySum = await hashUtil.hashFile("blake3", r.floppyFilePath);
		}
	};
	bin       = r => (r.floppyType ? `D:\\IN\\${r.inFile({backslash : true})}` : "ECHO");
	args      = () => ["A:"];
	msdosData = r => ({floppy : {filePath : path.join(r.cwd, "floppy.img"), type : r.floppyType}, keys : [xu.SECOND*10, "y", xu.SECOND, "Return"], timeout : xu.MINUTE*5});
	postExec  = async r =>
	{
		if(r.floppySum===await hashUtil.hashFile("blake3", r.floppyFilePath))
			return;

		await Deno.copyFile(r.floppyFilePath, path.join(r.f.outDir.absolute, "out.img"));
	};
	renameOut = true;
}
