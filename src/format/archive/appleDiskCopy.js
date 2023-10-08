import {Format} from "../../Format.js";

const _APPLE_DISK_COPY_MAGIC = ["Apple DiskCopy", "DiskCopy ", /^fmt\/625( |$)/];
export {_APPLE_DISK_COPY_MAGIC};

export class appleDiskCopy extends Format
{
	name       = "Apple DiskCopy";
	website    = "https://www.discferret.com/wiki/Apple_DiskCopy_4.2";
	magic      = _APPLE_DISK_COPY_MAGIC;
	converters = ["dd[bs:84][skip:1] -> dexvert"];
}
