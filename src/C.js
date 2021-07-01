"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu"),
	path = require("path");

const C = {};

// A list of family types. Order is the secondary order they will be matched in the case of multiple 'types' of matches (magic, etc, filename) across multiple categories
// If you add any here, you also need to update retromission.com msdos.styl
C.FAMILIES = ["archive", "document", "audio", "music", "video", "image", "3d", "font", "text", "executable", "rom", "other"];

// A priority to use if a file matches multiple times within a single family
C.PRIORITY =
{
	TOP      : 0,
	HIGH     : 1,
	STANDARD : 2,
	LOW      : 3,
	VERYLOW  : 4,
	LOWEST   : 5
};

C.FORMAT_DIR_PATH = path.join(__dirname, "format");

C.LOCK_CHECK_INTERVAL = XU.SECOND;

C.DEXSERV_HOST = "localhost";
C.DEXSERV_PORT = 17735;
C.DEXSERV_OK_RESPONSE = "a-ok";

C.TENSORSERV_PATH = "/mnt/ram/dexvert/tensor";
C.TENSORSERV_HOST = "localhost";
C.TENSORSERV_PORT = 17736;
C.TENSORSERV_OK_RESPONSE = "a-ok";

C.MATCH_MAX_GARBAGE_PROBABILITIES =
{
	magic    : 0.7,
	filename : 0.6,
	ext      : 0.6,
	fileSize : 0.01,
	fallback : 0.01
};

C.GARBAGE_DETECTED_DIR_PATH = "/mnt/dexvert/garbageDetected";
C.QEMU_INSTANCE_DIR_PATH = "/mnt/ram/dexvert/qemu";

C.BROKEN_IMAGE_HEX_DATA = "89504e470d0a1a0a0000000d4948445200000080000000800806000000c33e61cb00000006624b474400ff00ff00ffa0bda793000007e649444154789ced9d598c144518c77f3b3b1ec82e84851561e530410d284a44c1234262f08e4134f8200f5e892f02be299118828a068d313e29a031117d219c895114352a2831ec0262808807b80872392a2cee728e0fdf4c326c6666b7aabbaa7bbabf5f520f3b3bd5f5afeeff5477d7f11554a70e9800bc0c6c0076039d40de302deaa19c722cb22827aec957fd3b916bb41e5800dc805c432ba6005b2c44a801e255ffedc0f44a8564ca7cd608ac06d601e32c842bf1620cb00c58093474ff6777030c07be03a6bad7a578661a726d87957e586a8006e023e06a8fa214bf8c05d602fd8a1f941ae083c2179464330678aff847d100f7a0cd7e9a7800b813c40075c02b91ca51a26021509741def3af89588ce29f6b81f119b4e94f335333c0a4a85528913139035c1ab50a25325ab2c0e0100e741ad80be42afcbfdde298ed409bb5a2781176fd9b900e9dacb522612804eb673e00cc2c0852fcd204cc020e12ec1a5a676c0386b8aea5d2234381cd7836c001f4e2c789a1c0213c1a60a6976a2926ccc693014ea1f7fc3832107918776e805f3d554831673786d7b3dc84909ef82714a98a0b2abd8657c4c600798b3c8a1f8caf8d8d019404a10648396a8094a30648395960b1611e9b810dc50fab48ce009aa2288aa2288aa22889a10198036c023ab01bc3ce015f028f02f55ed59f4b3df058414b0ebbba7420e7e259a0af5ff9fe1907fc8edd89aa94be259c89ada65c026cb4d05b2ded41166c249211d84f5bea29b50217faab0a7d08360faf5a3a882cd34f1c2b7073c28a698ebfaaf09cc37ae491800e8962307006b7276d0f01e2e11850877487bbaccb19e416e31c5f8341377a286b0485850e8e69a15b940d071417ed3a278b7900a37624029509cd86dfb7e562609fe3327cd5c5a69cb9183e3f6481270d0b69c3dc00be5a1a1fe5f8aa8bcdebed3460bc49069d0f9072d40029470d9072d40029470d9072d40029470d9072d40029470d9072d40029470d90727c19a0cb53399d1eca48525dbc19608f87328ab10a5db31719af77cd6e0f657833c046e02fc7657c0d1c735c06c051e01bc7651c01be775c06e0cf00a7701b923e0fbce0f0f8dd79b150a62b1620e7cc0ba6d3955a2dcbc920ab575d4ca17ade525310e605d05b2dadc0fe87d96a519e3703804c405980ddde83e5d261646d40543c5ed010465d3a919625c83a076303d461de94b501d70710093249f43e64ff1a9bc51039644fc38f91851551d200dc8bac79b0899fd801ec4036ec3a18504b2b863382c06f0ba0b8c5b805d08ea094a30648396a8094a30648396a8094a30648396a8094a306483941b71dab15fa2191374623fb248e40165f9e07f4477e087f23c3bc87813f0ae927a4c7d1f548666424d500038029c01dc0646014c16207ec05d6039f019f229b662586a474055f808c2f2c034ee266a4aef41c3c8decd31327623f1ae882fe4884ad23b8bde8e55217125f212e317d526580bec04bd8879a0b339d04de060639ad71cfa4c6000f21f7e5a82f7cf79443b6738deaed2af1066804deafa02b4ee90bfcc42bea4ea20d3006f8b9971ae3900e216f203e49ec7c809b9059bfa3a216624033f2daf870d442aa510bfd007702ab093f126827f027f02f7016e93b68466e3361713eb01479605d12e2714325ceb78009c85cff309ae49dc042a4afa0dafd7910d281341f99ff783684b24f2311bc5c93a8678091049f717b0278078b8992255c09bc41f0d7cd4e6062001dbd213106c82251c0839cf065c065216a1a0cbc45b090b7bf211d57ae488c01e65be82aa61c6e9bdb5b09d607f1a1436d8930c028a4e9b639b9bb80cb1deb03690d82ec15709b235d8930806d58f99dc010c7da4a690436586add829bdec29a37c0440b3d79e46131ccfb7d6f69c2be73ca45ff40cd1b60a9859eb3485f41548cc5ee96b5d181969a36403332bc6aaae75d477a4c98875d2b705dc83a6ada00b32cb4fc87a79d357aa00fb01f73fd6f86aca3a6c702eeb6c8b384784ccfea045eb5c86753e7d089430bd007386ea165ac032db63461770b0b7380cbb805c8028b0d0b690f4b6d0913808b0cf36c057e74a0c5961cf00970bf61bec9c02f216958858c5fd41c4f61fecb792d12a5d5b1a9c7eb91282d10976780d11679d687ae223836d1c3ae0a5d85017131c01516797686ae2238bb308f216853f7d0888b014c63eb9cc6532045434e601eac72800b21bd252e06e867f8fd638809e248cef0fb8df8d9f1b42c713180e934ace34e54848369d4b27accdf801445511445511445512ca943d6b79bd08ef9f6f18a1fe66211ab200ec3c14a38d4f484102502d40029470d9072d40029c7c600918d5c293d627c6d6c0c10e9f8b55215abb885a6af81a7b0db1c4971cb20648e84f3d7c02c302304c14ab8ccc072cb39d316208f6c6f16451834a53c2dd84753b1ca940736a32688032dc87273dbeb689d318fc4c29b4dfc8226a7818148c0ea407194ea90756d4143b09d4166c3568aabbf0af301a4b9f889ace583b0eb3f101846b06d6601bab2c8e2ca91010f545f3846a5e3d82c571a4eb0e85e7122aef5df9701f6392e44892ffb33480856259d7c9501d644ad42898c35196013f043d44a14ef6c05366790d78139118b51fcf30c255dc16b8195118a51fcb21c5807e78e063e026c8b448ee2931dc013c53f4a0dd08184528f53d815255cb6017701478b1f741f0d6c076e466f07496439700bdde217941b0eee001e046e47061994da663bd2b24fa7ccd2f56a5bc67c8e74458e47225f4d42f6dd1d42f8dbb728e1d08504acdc8774f0ad41baa1f39532fc0f6274fa6b39c01d0d0000000049454e44ae426082";	// eslint-disable-line max-len

C.TEXT_MAGIC =
[
	"ASCII text", "ISO-8859 text", "UTF-8 Unicode text", "Non-ISO extended-ASCII text", "ReStructuredText file", "International EBCDIC text", "UTF-8 Unicode text", "Printable ASCII", "Unicode text, UTF-8 text",
	"Algol 68 source, ISO-8859 text"	// Algol 68 is often mis-identified, usually confused with Pascal files. Just treat it as regular text
];

// These magics are VERY untrustworthy and nothing should EVER match on them (but still keep them for record sakes)
C.UNTRUSTWORTHY_MAGIC =
[
	// FILE: Very weak checks:
	/^Apple DiskCopy 4.2 image/,
	/^assembler source/,
	/^basic-16 executable/,
	/^Clarion Developer/,
	/^diff output/,
	/^dBase I[IV]I? DBT/,
	/^DIY-Thermocam raw data/,
	/^Dyalog APL/,
	/^Hitachi SH/,
	/^HTML document/,
	/^iAPX 286 executable/,
	/^(little|big) endian ispell/,
	/^Java.*KeyStore$/,
	/^MacBinary II,/,
	/^mc68k executable/,
	/^MMDF mailbox$/,
	/^Motorola S-Record; binary data in text format$/,
	/^Novell LANalyzer capture file$/,
	/^PEX Binary Archive$/,
	/^Par archive data$/,
	/^Picasso 64 Image$/,
	/^OpenPGP Public Key/,
	/^OpenPGP Secret Key/,
	/^PGP key security ring/,
	/^PGP Secret Sub-key/,
	/^PGP symmetric key encrypted data/,
	/^PDP-11/,
	/^RDI Acoustic Doppler Current Profiler/,
	/^SysEx File/,
	/^StarOffice Gallery theme/,
	/^TeX font metric data/,
	/^troff or preprocessor input/,
	/^Targa image data/,
	/^Windows boot log/,
	/^Windows Precompiled iNF/,
	/^Zebra Metafile graphic/,

	// TRID: Checks just 1-3 bytes:
	/^Affix file$/,
	/^Agfa\/Matrix SCODL bitmap$/,
	/^Any Password data$/,
	/^Atari XE Executable$/,
	/^C64 Hires bitmap$/,
	/^Cardwar Cards deck$/,
	/^Commodore .+ BASIC .+ program$/,
	/^DEGAS low-res compressed bitmap$/,
	/^DEGAS med-res bitmap$/,
	/^DEGAS med-res compressed bitmap$/,
	/^DEGAS hi-res bitmap$/,
	/^DEGAS hi-res compressed bitmap$/,
	/^DICOM medical imaging bitmap/,
	/^Digital Micrograph Script$/,
	/^DiskDupe 5\.12 disk image$/,
	/^Generic INI configuration$/,
	/^GIF bitmap \(generic\)$/,
	/^GNU Privacy Guard public keyring \(generic\)$/,
	/^GraphiCode Programmable Device Format$/,
	/^Interpaint bitmap$/,
	/^ISIS sketch$/,
	/^Jupiter Ace snapshot$/,
	/^Koala Paint/,
	/^Luxor ABC80 tokenized BASIC source$/,
	/^Maple Common Binary file \(generic\)$/,
	/^Microsoft Help \(old\)$/,
	/^MP3 audio/,
	/^MSX2 ROM Image$/,
	/^null bytes$/,
	/^OMF - Relocatable Object Module Format$/,
	/^OS\/2 Bitmap Graphics Array \(generic\)$/,
	/^PGN \(Portable Gaming Notation\) Compressed format$/,
	/^Philips Respironics M-Series data format$/,
	/^PrintFox\/Pagefox bitmap/,
	/^Python Pickle serialized data/,
	/^That's Write document$/,
	/^VGAPaint 386 module$/,
	/^WordPerfect document \(Amiga\)$/,
	/^XBase DataBase \(generic\)$/,
	/^Z-Code V\d adventure for Infocom Z-Machine$/,
	
	// TRID: Checks for just zeroes or nearly all zeroes:
	/^Adobe PhotoShop Brush$/,
	/^bCAD Drawing$/,
	/^Dyalog APL transfer$/,
	/^Install Maker( Pro)? project$/,
	/^Intel CPU Microcode$/,
	/^Inset PIX bitmap$/,
	/^Lotus 123\/Symphony worksheet\/format\/configuration \(V1-V2\)$/,
	/^MacBinary [12]$/,
	/^Memo File Apollo Database Engine$/,
	/^OS\/2 Dynamic Link Library \(no DOS stub\)$/,
	/^Palantir WinTime Plan$/,
	/^Pegasus SPS encoded audio$/,
	/^Sybase iAnywhere database files$/,
	/^VXD Driver$/,
	/^Windows Device Dependent Bitmap$/,
	/^Windows Jump List$/,

	// TRID: Weak in some other way, such as global strings
	/^Amiga Disk image File \(generic\)$/,
	/^Dan Bricklin's Demo/,
	/^Scalable Vector Graphics \(var\.3\)$/
];

module.exports = C;
