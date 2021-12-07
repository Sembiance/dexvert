import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {dateParse, path} from "std";

export class xdftool extends Program
{
	website          = "http://lallafa.de/blog/amiga-projects/amitools/";
	package          = "app-arch/amitools";
	bin              = "xdftool";
	args             = r => [r.inFile(), "unpack", r.outDir()];
	filenameEncoding = "iso-8859-1";	// AmigaOS uses this: http://lclevy.free.fr/adflib/adf_info.html#p54
	renameOut        = false;
	
	// The sole purpose of this function is to load the xdfmeta file and then set the appropriate timestamps on all the output files
	post = async r =>
	{
		const xdfmetaFilePaths = await fileUtil.tree(r.outDir({absolute : true}), {regex : /\.xdfmeta$/});
		await xdfmetaFilePaths.parallelMap(async xdfmetaFilePath =>
		{
			const xdfmetaRaw = await Deno.readTextFile(xdfmetaFilePath);

			// Meta format: https://github.com/cnvogelg/amitools/blob/974ad59645454e2490ce155407135e1cffbe61bb/amitools/fs/MetaDB.py
			const lines = xdfmetaRaw.split("\n");
			if(!lines || lines.length===0)
				return this();

			const volParts = (lines[0].match(/^(?<volName>[^:]+):(?<dosType>[^,]+),(?<ts>[^,]+),/) || {groups : {}}).groups;
			if(!volParts.volName)
				return this();

			let volDate = dateParse(volParts.ts, "dd.MM.yyyy HH:mm:ss.SS");
			if(volDate.getFullYear()>=2020)
				volDate = new Date(r.f.input.ts);

			await lines.slice(1).parallelMap(async line =>
			{
				const parts = (line.match(/^(?<pathName>[^:]+):(?<protect>[^,]+),(?<ts>[^,]+),(?<comment>.*)$/) || {groups : {}}).groups;
				if(!parts.pathName || !parts.ts)
					return;

				let fileDate = dateParse(parts.ts, "dd.MM.yyyy HH:mm:ss.SS");
				if(fileDate.getFullYear()>=2020)
					fileDate = volDate;

				const outputFile = r.f.files.new.find(file => file.absolute===path.join(r.outDir({absolute : true}), volParts.volName, parts.pathName));
				if(outputFile)
					await outputFile.setTS(fileDate.getTime());
			});
		});
	};
}
