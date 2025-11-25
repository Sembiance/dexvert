const decoder = new TextDecoder('Shift_JIS');

const tablePc98DependentChars = Object.freeze({
	0x857b: '¥',	// YEN SIGN
	0x859e: '‾',	// OVERLINE

	0x85de: 'ヰ',
	0x85df: 'ヱ',
	0x85e0: 'ヮ',
	0x85e1: 'ヵ',
	0x85e2: 'ヶ',
	0x85e3: 'ヴ',
	0x85e4: 'ガ',
	0x85e5: 'ギ',
	0x85e6: 'グ',
	0x85e7: 'ゲ',
	0x85e8: 'ゴ',
	0x85e9: 'ザ',
	0x85ea: 'ジ',
	0x85eb: 'ズ',
	0x85ec: 'ゼ',
	0x85ed: 'ゾ',
	0x85ee: 'ダ',
	0x85ef: 'ヂ',
	0x85f0: 'ヅ',
	0x85f1: 'デ',
	0x85f2: 'ド',
	0x85f3: 'バ',
	0x85f4: 'パ',
	0x85f5: 'ビ',
	0x85f6: 'ピ',
	0x85f7: 'ブ',
	0x85f8: 'プ',
	0x85f9: 'ベ',
	0x85fa: 'ペ',
	0x85fb: 'ボ',
	0x85fc: 'ポ',
});

function isPc98DependentChars(cp932code) {
	return (0x8540 <= cp932code && cp932code <= 0x86ff);
}

export function decodeNec932(bytes) {
	// Checks whether the bytes seem to contain PC-98 dependent characters.
	if ([...bytes].some((e, i, a) => (i > 0) && isPc98DependentChars((a[i - 1] << 8) | e))) {	// It allows false positive.
		// Separates from the bytes to each character code according to Shift_JIS encoding.
		let leadingByte = -1;
		const charArrays = [...bytes].reduce((p, c) => {
			if (leadingByte >= 0) {
				p.push([leadingByte, c]);
				leadingByte = -1;
			} else if ((0x81 <= c && c <= 0x9f) || (0xe0 <= c && c <= 0xfc)) {
				leadingByte = c;
			} else {
				p.push([c]);
			}
			return p;
		}, []);

		// Replaces PC-98 dependent characters into Unicode's ones.
		return charArrays.map((e) => {
			const cp932code = e.reduce((p, c) => (p << 8) | c);
			if (tablePc98DependentChars[cp932code]) {
				return tablePc98DependentChars[cp932code];
			} else if ((0x86a2 <= cp932code && cp932code <= 0x86ee)) {	// PC-98 dependent full-width box drawing
				return String.fromCodePoint(cp932code - 0x61a2);
			} else if (0x8643 <= cp932code && cp932code <= 0x868f) {	// PC-98 dependent multi-byte half-width box drawing
				return String.fromCodePoint(cp932code - 0x6143);
			} else if (0x859f <= cp932code && cp932code <= 0x85dd) {	// PC-98 dependent multi-byte half-width katakana
				return String.fromCodePoint(cp932code + 0x79c2);
			} else if (0x8540 <= cp932code && cp932code <= 0x859e) {	// PC-98 dependent multi-byte half-width JIS X 0201
				return String.fromCodePoint(cp932code - 0x851f);
			} else {
				return decoder.decode(new Uint8Array(e));
			}
		}).join('');

	} else {
		return decoder.decode(bytes);
	}
}
