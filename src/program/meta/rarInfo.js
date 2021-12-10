import {Program} from "../../Program.js";

export class rarInfo extends Program
{
	website = "https://www.rarlab.com/rar_add.htm";
	package = "app-arch/unrar";
	bin     = "unrar";
	args    = r => ["lt", r.inFile()];
	post    = r =>
	{
		const meta = {files : {}};
		let fileName = null;
		let seenArchive = false;
		const NUMBER_FIELDS = ["size", "packedSize"];
		r.stdout.trim().split("\n").forEach(line =>
		{
			const {k, v} = (line.trim().match(/^\s*(?<k>[^:]+):\s*(?<v>.+)$/) || {groups : {}}).groups;
			if(!k || !v)
				return;

			const key = k.trim().toCamelCase();
			if(key==="archive")
				seenArchive = true;
			if(!seenArchive)
				return;
			const val = NUMBER_FIELDS.includes(key) ? +v.trim() : v.trim();

			if(key==="name")
			{
				fileName = val;
				meta.files[fileName] = {};
			}
			else if(fileName)
			{
				meta.files[fileName][key] = val;
			}
			else
			{
				meta[key] = val;
			}
		});

		if(Object.values(meta.files).some(file => (file.flags || "").toLowerCase().includes("encrypted")))
			meta.passwordProtected = true;

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}

