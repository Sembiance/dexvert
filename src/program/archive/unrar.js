import {Program} from "../../Program.js";

export class unrar extends Program
{
	website = "https://www.rarlab.com/rar_add.htm";
	package = "app-arch/unrar";
	bin     = "unrar";
	args    = r => ["x", "-p-", r.inFile(), r.outDir()];
	post    = r =>
	{
		if(r.stdout.length>0)
		{
			const commentGroups = (r.stdout.replaceAll("\n", "§").replaceAll("\r", "†").match(/Extracting from in\.rar§(?<comment>.+)§§Extracting /) || {groups : {}}).groups;
			if(commentGroups.comment)
				r.meta.comment = commentGroups.comment.replaceAll("§", "\n").replaceAll("†", "\r").trimChars("\n\r");	// don't trim anything other than newlines, to preserve comment spacing
		}
	};
	renameOut = false;
}
