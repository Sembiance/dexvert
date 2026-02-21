import {Format} from "../../Format.js";

export class appleDiskCopyNDIF extends Format
{
	name       = "Apple DiskCopy NDIF";
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="rohd" && macFileCreator==="ddsk";
	priority   = this.PRIORITY.TOP;
	converters = ["undiskcopy -> dexvert[skipVerify][bulkCopyOut]"];
}
