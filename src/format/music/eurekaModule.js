import {xu} from "xu";
import {Format} from "../../Format.js";

export class eurekaModule extends Format
{
	name         = "Eureka Module";
	website      = "http://fileformats.archiveteam.org/wiki/Eureka_Packer_module";
	ext          = [".eureka", ".eu"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
