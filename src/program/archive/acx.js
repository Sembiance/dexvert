import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil, fileUtil} from "xutil";
import {_proDOSTypeCodeToPretty} from "./cadius.js";
import {dateParse, path} from "std";

export class acx extends Program
{
	website   = "https://github.com/AppleCommander/AppleCommander";
	package   = "app-arch/AppleCommander";
	bin       = "acx";
	args      = r => ["x", "--suggested", "-d", r.inFile(), "-o", r.outDir()];

	renameOut = false;
	chain     = "unHexACX";

	// acx doesn't create subdiretories (apple2MG/SDGS\ 96.2mg), instead naming things as SDA96:A, so let's fix that
	postExec = async r =>
	{
		const subDirFilePaths = await fileUtil.tree(r.outDir({absolute : true}), {nofile : true, regex : /.+:.+/});
		for(const subDirFilePath of subDirFilePaths)
		{
			const dirParts = path.basename(subDirFilePath).split(":");
			const newDirPath = path.join(path.dirname(subDirFilePath), ...dirParts);
			await Deno.mkdir(path.dirname(newDirPath), {recursive : true});
			await Deno.rename(subDirFilePath, newDirPath);
		}
	};

	// For 'ProDOS' files (appleDOSDiskImage/111a_Playboy.dsk), acx/unHexACX doesn't set dates, but acx knows about them if I do a listing, so this function will do a listing and set proper dates
	chainPost = async r =>
	{
		const currentYear = new Date().getFullYear();
		const {stdout} = await runUtil.run("acx", ["ls", "-r", "-d", r.inFile()], {cwd : r.cwd});
		r.meta.fileMeta = {};
		const dirChain = [];
		for(const line of stdout.split("\n"))
		{
			const {volumeName} = line.match(/^Name:\s+\/(?<volumeName>[^/]+)\/.*$/)?.groups || {};
			if(volumeName)
			{
				if(volumeName!=="APPLECOMMANDER")
					r.meta.volumeName = volumeName;
				continue;
			}

			const {dirName, indents} = line.match(/^\*?(?<indents>\s+)(?<dirName>\S+)\s+DIR.+$/)?.groups || {};
			if(dirName)
			{
				while(dirChain.length>((indents.length/2)-1))
					dirChain.pop();
				dirChain.push(dirName);
				
				continue;
			}

			const {filename, proDOSTypeCode, month, day, year, proDOSTypeAux} = line.match(/^\*?\s+(?<filename>\S+)\s+(?<proDOSTypeCode>\S+)\s+\S+\s+(?<month>\d+)\/(?<day>\d+)\/(?<year>\d+)\s\d+\/\d+\/\d+\s+\S+(?:\s+A=\$(?<proDOSTypeAux>[\dA-F]{4}))?.*$/)?.groups || {};
			if(!filename)
				continue;
			
			const meta = {};
			
			//r.xlog.debug`acx parsing line: ${line}\n\t${{proDOSTypeCode, proDOSTypeAux}}`;
			if(proDOSTypeCode)
			{
				meta.proDOSTypeCode = proDOSTypeCode;
				meta.proDOSTypePretty = _proDOSTypeCodeToPretty(proDOSTypeCode);
			}
			if(proDOSTypeAux)
				meta.proDOSTypeAux = proDOSTypeAux;

			if((+year)<currentYear)
				meta.when = dateParse(`${day}.${month}.${(+year)<1970 ? currentYear : year} 00:00:00`, "dd.MM.yyyy HH:mm:ss");

			if(Object.keys(meta).length>0)
				r.meta.fileMeta[`${dirChain.join("/")}${dirChain.length ? "/" : ""}${filename}`] = meta;
		}

		for(const outputFile of r.f.files.new || [])
		{
			const relPath = path.relative(r.outDir(), outputFile.rel);
			if(r.meta.fileMeta[relPath]?.when)
			{
				outputFile.setTS(r.meta.fileMeta[relPath]?.when.getTime());
			}
			else
			{
				// acx adds various extra extensions like .PNG, .bas, .csv when it converts a file, so we try stripping the extension to see if we match then
				const relPathModified = path.join(path.dirname(relPath), path.basename(relPath, path.extname(relPath)));
				if(r.meta.fileMeta[relPathModified]?.when)
					outputFile.setTS(r.meta.fileMeta[relPathModified]?.when.getTime());
			}
		}
	};
}
