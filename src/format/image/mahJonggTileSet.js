import {Format} from "../../Format.js";

//const VALID_SIZES = [800, 801, 832, 833, 8000, 8001, 8064, 8065, 33600, 33601, 33664, 33665, 34400, 34401, 34496, 34497, 35200, 35201, 36000, 36001, 36032, 36033, 36800, 36801, 36864, 36865, 37600, 37601, 37696, 37697, 38400, 38401, 39200, 39201, 39232, 39233, 40000, 40001, 40064, 40065, 40800, 40801, 40896, 40897, 41600, 41601, 42400, 42401, 42432, 42433, 43200, 43201, 43264, 43265, 44000, 44001, 44096, 44097, 44800, 44801, 45600, 45601, 45632, 45633, 46400, 46401, 46464, 46465, 47200, 47201, 47296, 47297, 48000, 48001];	// eslint-disable-line max-len

export class mahJonggTileSet extends Format
{
	name           = "Mah Jonngg Tile Set";
	website        = "http://fileformats.archiveteam.org/wiki/Mah_Jongg_(Nels_Anderson)_tile_set";
	ext            = [".til"];
	forbidExtMatch = true;
	magic          = ["deark: mahj_na_til"];
	converters     = ["deark[module:mahj_na_til]"];
}
