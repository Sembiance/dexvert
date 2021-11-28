import {Program} from "../../Program.js";

export class foremost extends Program
{
	website       = "http://foremost.sourceforge.net/";
	gentooPackage = "app-forensics/foremost";
	bin           = "foremost";
	args          = r => [`-o${r.outDir()}`, r.inFile()];
	post          = async r => await r.f.remove("new", r.f.files.new.find(file => file.base==="audit.txt"), {unlink : true});
}
