# Expert lab recipe (seed 1, level 2)

By-product of the reference run: what the scripted expert did, in order, with lab time.

- OPA wavelength 1300 nm. Parts bought: DL-M25 manual delay stage, 4 x MIR-1 mirror, 1 x PER-1 periscope, CAM-VSWIR, GAP-TPA (EUR 8250; C_min = EUR 7300)
- Lab time: 122.2 min of 240 (50.9%), 115 tool calls
- Result: eta = 0.9969, R = 0.8975, O = 0.9972, |dt| = 3.2 fs

| # | t (min) | tool | args |
|---|---|---|---|
| 0 | 0.0 | read_manual | `{"device": "table"}` |
| 1 | 0.0 | read_manual | `{"device": "opa"}` |
| 2 | 0.0 | read_manual | `{"device": "delay_stage"}` |
| 3 | 0.0 | read_manual | `{"device": "sample_mount"}` |
| 4 | 15.0 | buy | `{"items": {"DL-M25": 1, "MIR-1": 4, "PER-1": 1, "GAP-TPA": 1, "CAM-VSWIR": 1}}` |
| 5 | 20.1 | place | `{"part": "sample", "x": 1200.0, "z": 600.0, "height": 120.0, "yaw_deg": 0.0}` |
| 6 | 20.2 | unblock | `{"arm": "opa"}` |
| 7 | 25.4 | place | `{"part": "periscope-1", "x": 2050.0, "z": 935.0, "height": 120.0, "yaw_deg": 180.0, "height_in": 158.0}` |
| 8 | 25.9 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 9 | 26.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 10 | 26.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": 5.0988}` |
| 11 | 27.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 12 | 27.9 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": 5.0988}` |
| 13 | 28.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 14 | 29.0 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -7.0432}` |
| 15 | 29.5 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -5.5161}` |
| 16 | 30.0 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 17 | 30.5 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -0.7803}` |
| 18 | 31.0 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -0.6926}` |
| 19 | 31.5 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 20 | 36.5 | place | `{"part": "mirror-1", "x": 1461.6295090390227, "z": 935.0, "height": 120.0, "yaw_deg": -45.0}` |
| 21 | 37.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 22 | 37.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 23 | 38.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 40.8884}` |
| 24 | 38.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 25 | 39.0 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 40.8884}` |
| 26 | 39.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 27 | 40.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": -16.4774}` |
| 28 | 40.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -20.0}` |
| 29 | 41.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 30 | 41.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -20.0}` |
| 31 | 42.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 32 | 47.0 | place | `{"part": "mirror-2", "x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0, "yaw_deg": 157.5}` |
| 33 | 47.5 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 34 | 48.0 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 35 | 48.5 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 11.1111}` |
| 36 | 49.0 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 37 | 49.6 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 11.1111}` |
| 38 | 50.1 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 39 | 50.6 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 10.5976}` |
| 40 | 51.1 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -15.0815}` |
| 41 | 51.6 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 42 | 52.1 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.4836}` |
| 43 | 52.6 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 2.5912}` |
| 44 | 53.1 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 45 | 53.3 | unblock | `{"arm": "800nm"}` |
| 46 | 58.3 | place | `{"part": "stage", "x": 873.6118318204308, "z": 309.0, "height": 120.0, "yaw_deg": 180.0}` |
| 47 | 58.8 | ir_card | `{"x": 1546.4823227814081, "z": 324.0, "height": 120.0}` |
| 48 | 63.8 | place | `{"part": "mirror-3", "x": 1546.4823227814081, "z": 325.9, "height": 119.3, "yaw_deg": 225.0}` |
| 49 | 64.3 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 50 | 64.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 51 | 65.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 41.4466}` |
| 52 | 65.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 53 | 66.3 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": 41.4466}` |
| 54 | 66.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 55 | 67.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -20.0}` |
| 56 | 67.8 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -20.0}` |
| 57 | 68.3 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 58 | 68.8 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -18.8026}` |
| 59 | 69.3 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -15.7699}` |
| 60 | 69.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 61 | 70.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 3.1506}` |
| 62 | 70.8 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -4.5996}` |
| 63 | 71.3 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 64 | 76.3 | place | `{"part": "mirror-4", "x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0, "yaw_deg": 112.5}` |
| 65 | 76.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 66 | 77.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 67 | 77.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 7.6923}` |
| 68 | 78.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 69 | 78.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 7.6923}` |
| 70 | 79.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 71 | 79.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 10.9505}` |
| 72 | 80.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -7.3816}` |
| 73 | 80.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 74 | 81.4 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.7611}` |
| 75 | 81.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.2437}` |
| 76 | 82.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 77 | 82.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.7526}` |
| 78 | 83.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.5003}` |
| 79 | 83.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 80 | 84.5 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -1.0219}` |
| 81 | 85.0 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.1112}` |
| 82 | 85.5 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 83 | 85.6 | block | `{"arm": "800nm"}` |
| 84 | 85.8 | view_camera | `{"plane": "sample"}` |
| 85 | 85.9 | unblock | `{"arm": "800nm"}` |
| 86 | 86.0 | view_camera | `{"plane": "sample"}` |
| 87 | 86.2 | view_camera | `{"plane": "sample"}` |
| 88 | 86.8 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.3}` |
| 89 | 87.1 | view_camera | `{"plane": "sample"}` |
| 90 | 87.2 | view_camera | `{"plane": "sample"}` |
| 91 | 87.8 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.3}` |
| 92 | 88.1 | view_camera | `{"plane": "sample"}` |
| 93 | 88.2 | view_camera | `{"plane": "sample"}` |
| 94 | 88.8 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.5351}` |
| 95 | 89.3 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.0537}` |
| 96 | 89.6 | view_camera | `{"plane": "sample"}` |
| 97 | 89.8 | view_camera | `{"plane": "sample"}` |
| 98 | 90.4 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.0683}` |
| 99 | 90.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.0429}` |
| 100 | 91.1 | view_camera | `{"plane": "sample"}` |
| 101 | 91.3 | view_camera | `{"plane": "sample"}` |
| 102 | 91.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.0099}` |
| 103 | 92.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.0106}` |
| 104 | 92.6 | view_camera | `{"plane": "sample"}` |
| 105 | 92.8 | view_camera | `{"plane": "sample"}` |
| 106 | 101.2 | scan | `{"start_mm": 11.0, "end_mm": 14.0, "step_mm": 0.025, "t_int": 1.0}` |
| 107 | 106.7 | scan | `{"start_mm": 9.0, "end_mm": 11.0, "step_mm": 0.025, "t_int": 1.0}` |
| 108 | 112.2 | scan | `{"start_mm": 14.0, "end_mm": 16.0, "step_mm": 0.025, "t_int": 1.0}` |
| 109 | 121.6 | scan | `{"start_mm": 15.3385, "end_mm": 15.5615, "step_mm": 0.002, "t_int": 2.0}` |
| 110 | 121.7 | move_stage | `{"position_mm": 15.39007}` |
| 111 | 121.8 | move_stage | `{"position_mm": 15.44007}` |
| 112 | 122.0 | view_camera | `{"plane": "sample"}` |
| 113 | 122.2 | view_camera | `{"plane": "sample"}` |
| 114 | 122.2 | submit | `{}` |
