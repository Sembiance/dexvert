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
		
		const acxInfo = xu.parseJSON((await runUtil.run("acx", ["ls", "--detail", "--json", "-r", "-d", r.inFile()], {cwd : r.cwd})).stdout)?.disks?.[0];
		if(!acxInfo)
			return;

		r.meta.fileMeta = {};
		const volumename = acxInfo.diskName?.trimChars("/:");
		if(volumename && volumename!=="APPLECOMMANDER")
			r.meta.volumeName = volumename;

		const dirs = {};
		for(const file of acxInfo.files || [])
		{
			const subPath = file.directory?.length && file.directory!=="0002" ? path.join(dirs[file.directory], file.name) : file.name;
			if(file.type==="DIR")
			{
				dirs[file.keyBlock] = subPath;
				continue;
			}

			const meta = {};
			for(const prop of [file.modified, file.created])
			{
				for(const regex of [/^(?<month>\d\d)\/(?<day>\d\d)\/(?<year>\d{4})/, /^(?<day>\d\d)-(?<monthName>[A-Za-z]{3})-(?<yearPart>\d\d)/])
				{
					const {month, monthName, day, year, yearPart} = prop?.match(regex)?.groups || {};
					const yearFull = +year || 1900 + (+yearPart);
					if(yearFull && yearFull<currentYear && yearFull>=1970)
						meta.when = dateParse(`${day}.${month || {Jan : "01", Feb : "02", Mar : "03", Apr : "04", May : "05", Jun : "06", Jul : "07", Aug : "08", Sep : "09", Oct : "10", Nov : "11", Dec : "12"}[monthName]}.${yearFull} 00:00:00`, `dd.MM.yyyy HH:mm:ss`);
				}
			}
			
			if(acxInfo.format==="ProDOS")
			{
				const {auxType} = file.auxType?.match(/^A?=?\$(?<auxType>[\dA-F]{4})/)?.groups || {};
				if(auxType)
					meta.proDOSTypeAux = auxType;
				if(file?.type?.length)
				{
					meta.proDOSTypeCode = file.type;
					meta.proDOSTypePretty = _proDOSTypeCodeToPretty(file.type);
				}
			}

			if(Object.keys(meta).length>0)
				r.meta.fileMeta[subPath] = meta;
		}

		for(const outputFile of r.f.files.new || [])
		{
			const relPath = path.relative(r.outDir(), outputFile.rel);
			for(const subPath of [relPath, path.join(path.dirname(relPath), path.basename(relPath, path.extname(relPath)))])
			{
				if(r.meta.fileMeta[subPath]?.when)
					outputFile.setTS(r.meta.fileMeta[subPath]?.when.getTime());
			}
		}
	};
}
