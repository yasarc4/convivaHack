STATES = dict([r.split(',') for r in '''AK,Alaska
AL,Alabama
AR,Arkansas
AZ,Arizona
CA,California
CO,Colorado
CT,Connecticut
DC,District of Columbia
DE,Delaware
FL,Florida
GA,Georgia
HI,Hawaii
IA,Iowa
ID,Idaho
IL,Illinois
IN,Indiana
KS,Kansas
KY,Kentucky
LA,Louisiana
MA,Massachusetts
MD,Maryland
ME,Maine
MI,Michigan
MN,Minnesota
MO,Missouri
MS,Mississippi
MT,Montana
NC,North Carolina
ND,North Dakota
NE,Nebraska
NH,New Hampshire
NJ,New Jersey
NM,New Mexico
NV,Nevada
NY,New York
OH,Ohio
OK,Oklahoma
OR,Oregon
PA,Pennsylvania
PR,Puerto Rico
RI,Rhode Island
SC,South Carolina
SD,South Dakota
TN,Tennessee
TX,Texas
UT,Utah
VA,Virginia
VT,Vermont
WA,Washington
WI,Wisconsin
WV,West Virginia
WY,Wyoming'''.split('\n')])

ASSETS = ['LIVE | NBA Basketball | Toronto vs Michigan',
         'LIVE | Ashes Tour | Australia vs England Secnd Test',
         'LIVE | NFC | Semi Final',
         'RECORDED | UEFA Championship | Liverpool vs Manu',
         'LIVE | Sports News',
         'RECORDED | WWE | Smackdown',
         'LIVE | Live Debate | Economy Analysis']
DEVICE_COLORS = dict(
    MobileAndroid="#FFEDA0",
    SamsungTV="#FA9FB5",
    Browser="#A1D99B",
    App="#67BD65",
    PS="#BFD3E6",
    Xbox="#B3DE69",
    AppleTV="#FDBF6F",
    FireTV="#FC9272",
    Chromecast="#D0D1E6",
    iPad="#ABD9E9",
    iPhone="#3690C0",
    RokuTV="#F87A72",
    AndroidTV="#CA6BCC",
    Others="#DD3497",
    Unknown="#4EB3D3"
)
DEVICES = list(DEVICE_COLORS.keys())
