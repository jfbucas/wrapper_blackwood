﻿
namespace EternityII_Solver
{
    public struct Piece
    {
        public ushort PieceNumber { get; set; }
        public byte TopSide { get; set; }
        public byte RightSide { get; set; }
        public byte BottomSide { get; set; }
        public byte LeftSide { get; set; }
        public byte PieceType() // 2 for corners, 1 for sides, and 0 for middles
        {
            if (PieceNumber >= 1 && PieceNumber <= 4)
                return 2;
            else if (PieceNumber >= 5 && PieceNumber <= 60)
                return 1;

            return 0;
        }
    }

    public struct RotatedPiece
    {
        public ushort PieceNumber { get; set; }
        public byte Rotations { get; set; }
        public byte TopSide { get; set; }
        public byte RightSide { get; set; }
        public byte Break_Count { get; set; }
        public byte Heuristic_Side_Count { get; set; }
    }

    public struct RotatedPieceWithLeftBottom
    {
        public ushort LeftBottom { get; set; }
        public int Score { get; set; }
        public RotatedPiece RotatedPiece { get; set; }
    }

    public struct SearchIndex
    {
        public byte Row { get; set; }
        public byte Column { get; set; }
    }
}
