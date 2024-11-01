import {Format} from "../../Format.js";

export class irixIDBArchive extends Format
{
	name         = "IRIX IDB/SW Archive";
	website      = "http://fileformats.archiveteam.org/wiki/IRIX_software_distribution_format";
	ext          = [".idb"];
	magic        = ["IRIX software distribution format Installation DB", "Archive: SW"];
	keepFilename = true;
	auxFiles     = (input, otherFiles) => (otherFiles.length>0 ? otherFiles : false);	// IDB references various other files, usually with a .sw extension, but not always
	converters   = ["irixswextract"];
}
