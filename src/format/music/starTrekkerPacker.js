import {xu} from "xu";
import {Format} from "../../Format.js";

export class starTrekkerPacker extends Format
{
	name         = "StarTrekker Packer Module";
	ext          = [".stp", ".stpk"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
