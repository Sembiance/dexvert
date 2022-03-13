import {Program} from "../../Program.js";

export class unrar extends Program
{
	website = "https://www.rarlab.com/rar_add.htm";
	package = "app-arch/unrar";
	bin     = "unrar";
	args    = r => ["x", "-p-", "-idndp", "-y", r.inFile(), r.outDir()];
	post    = r =>
	{
		if(r.stdout.length>0)
		{
			const commentGroups = (r.stdout.replaceAll("\n", "§").replaceAll("\r", "†").match(/Extracting from in\.rar§(?<comment>.+)§/) || {groups : {}}).groups;
			if(commentGroups.comment)
			{
				const comment = commentGroups.comment.replaceAll("§", "\n").replaceAll("†", "\r").trimChars("\n\r");	// don't trim anything other than newlines, to preserve comment spacing
				if(comment.trim().length>0 && !comment.startsWith("Extracting from "))	// if empty line comment or multi-part rar archive, don't treat as comment (ZIPCRACK.RAR)
					r.meta.comment = comment;
			}
		}
	};
	renameOut = false;
}
