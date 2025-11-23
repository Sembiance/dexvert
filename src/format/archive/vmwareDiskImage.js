import {Format} from "../../Format.js";

export class vmwareDiskImage extends Format
{
	name       = "VMware disk image";
	website    = "http://fileformats.archiveteam.org/wiki/VMDK";
	ext        = [".vmdk"];
	magic      = ["VMware 4 Virtual Disk", "VMware4 disk image", "Format: VMWare image", "Format: VMWare Virtual Disk (VMDK)", "application/x-vmdk-disk"];
	auxFiles   = (input, otherFiles) => (otherFiles?.some(file => file.ext.toLowerCase()===".vmdk") ? otherFiles.filter(file => file.ext.toLowerCase()===".vmdk") : false);
	converters = ["sevenZip"];
}
