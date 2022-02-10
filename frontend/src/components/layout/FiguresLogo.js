import React from 'react';

export default function FiguresLogo({ version = 'negative', width='80px' }) {

  console.log(version);
  const mainColor = (version === 'negative') ? '#ffffff' : '#000000';

  return (
    <svg version="1.1" id="Layer_1" x="0px" y="0px" width={width} viewBox="39 -9.8 113.4 52.6" xmlSpace="preserve">
      <polygon id="XMLID_85_" class="st0" fill="none" stroke={mainColor} strokeWidth="1.1339" strokeMiterlimit="10" points="61.6,-8.5 40,4 40,29 45,26.1 45,6.9 61.6,-2.7 78.3,6.9 78.3,26.1 83.3,29 83.3,4 "/>
      <polygon id="XMLID_68_" class="st0" fill="none" stroke={mainColor} strokeWidth="1.1339" strokeMiterlimit="10" points="78.3,26.1 61.6,35.7 45,26.1 40,29 61.6,41.5 83.3,29 "/>
      <polygon id="XMLID_65_" class="st0" fill="none" stroke={mainColor} strokeWidth="1.1339" strokeMiterlimit="10" points="49.9,23.1 54.9,26 54.9,17.3 49.9,17.3 "/>
      <polygon id="XMLID_84_" class="st0" fill="none" stroke={mainColor} strokeWidth="1.1339" strokeMiterlimit="10" points="59,28.7 61.5,30.1 64,28.7 64,14.6 59,14.6 "/>
      <polygon id="XMLID_86_" class="st0" fill="none" stroke={mainColor} strokeWidth="1.1339" strokeMiterlimit="10" points="68.1,6.9 68.1,26 73.1,23.2 73.1,9.8 "/>
      <path id="XMLID_138_" class="st1" fill={mainColor} d="M95.6,9.6h6.9v1.7h-5v3.8h4.8v1.6h-4.8v5.9h-1.8L95.6,9.6L95.6,9.6z"/>
      <path id="XMLID_140_" class="st1" fill={mainColor}  d="M106.3,11h-2V9h2V11z M104.4,13.1h1.7v9.4h-1.7V13.1z"/>
      <path id="XMLID_143_" class="st1" fill={mainColor}  d="M117.1,22.1c0,2.9-1.5,4.5-4.9,4.5c-1,0-1.9-0.1-3.4-0.6l0.2-1.6c1.3,0.6,2.1,0.9,3.4,0.9 c1.8,0,2.9-1.2,2.9-3.2v-0.9l0,0c-0.7,1-2,1.5-3.2,1.5c-2.7,0-4-2.2-4-4.6s1.4-5,4.2-5c1.7,0,2.6,0.6,3.1,1.6l0,0v-1.4h1.6v8.8 H117.1z M115.3,17.9c0-2-0.9-3.6-2.8-3.6c-1.8,0-2.6,1.9-2.6,3.5c0,1.8,1,3.3,2.6,3.3C114.2,21.1,115.3,19.7,115.3,17.9z"/>
      <path id="XMLID_146_" class="st1" fill={mainColor}  d="M127.7,22.5H126V21l0,0c-0.5,1.1-1.8,1.7-3.1,1.7c-2.4,0-3.5-1.5-3.5-4v-5.6h1.7V18 c0,2.2,0.5,3.3,2,3.4c2,0,2.9-1.6,2.9-3.9v-4.4h1.7V22.5z"/>
      <path id="XMLID_148_" class="st1" fill={mainColor}  d="M130.1,13.1h1.6v1.5l0,0c0.5-1,1.5-1.7,2.5-1.7c0.5,0,0.8,0.1,1.1,0.1v1.6 c-0.3-0.1-0.7-0.2-1-0.2c-1.6,0-2.6,1.5-2.6,3.8v4.3H130v-9.4H130.1z"/>
      <path id="XMLID_150_" class="st1" fill={mainColor}  d="M143.9,22.2c-0.7,0.2-1.4,0.6-3,0.6c-3.3,0-4.9-2-4.9-5.1c0-2.8,1.8-4.8,4.4-4.8 c3.1,0,4.2,2.3,4.2,5.3h-6.7c0,1.9,1.5,3.1,3.1,3.1c1.1,0,2.5-0.6,2.9-0.9V22.2z M142.8,16.9c0-1.4-0.8-2.6-2.3-2.6 c-1.7,0-2.4,1.4-2.5,2.6H142.8z"/>
      <path id="XMLID_153_" class="st1" fill={mainColor}  d="M145.6,20.7c0.7,0.4,1.7,0.7,2.2,0.7c0.8,0,1.8-0.3,1.8-1.3c0-1.7-4.1-1.6-4.1-4.2
      c0-2,1.5-2.9,3.3-2.9c0.8,0,1.5,0.2,2.2,0.4l-0.1,1.5c-0.4-0.2-1.4-0.5-1.8-0.5c-0.9,0-1.7,0.4-1.7,1.1c0,1.9,4.1,1.4,4.1,4.4 c0,2-1.6,2.9-3.3,2.9c-0.9,0-1.8-0.1-2.6-0.5V20.7z"/>
  </svg>
  )
}