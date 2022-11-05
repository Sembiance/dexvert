import {Format} from "../../Format.js";

export class irixIDBArchive extends Format
{
	name         = "IRIX IDB/SW Archive";
	ext          = [".idb"];
	keepFilename = true;
	auxFiles     = (input, otherFiles) => (otherFiles.length>0 ? otherFiles : false);	// IDB references various other files, usually with a .sw extension, but not always
	converters   = ["irixswextract"];
}
