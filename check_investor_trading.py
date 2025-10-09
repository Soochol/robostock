"""Check investor_trading data in database"""
import sys
sys.path.insert(0, 'src')

from data.database import get_session
from data.models import InvestorTrading, Stock

with get_session() as session:
    # 삼성전자 수급 데이터 조회
    result = session.query(
        Stock.name,
        InvestorTrading.date,
        InvestorTrading.institutional_net_buy,
        InvestorTrading.foreign_net_buy,
        InvestorTrading.individual_net_buy,
        InvestorTrading.institutional_buying_strength,
        InvestorTrading.foreign_buying_strength
    ).join(Stock).filter(
        Stock.code == '005930'
    ).order_by(
        InvestorTrading.date.desc()
    ).limit(10).all()

    print("=" * 160)
    print(f"{'Stock':<15} {'Date':<15} {'Inst.NetBuy':>15} {'Foreign.NetBuy':>15} {'Indiv.NetBuy':>15} {'Inst.Strength':>15} {'Foreign.Strength':>15}")
    print("=" * 160)

    empty_count = 0
    for r in result:
        name, date, inst_net, foreign_net, indiv_net, inst_str, foreign_str = r

        # 모든 값이 0이거나 None인지 체크
        if (not inst_net or inst_net == 0) and (not foreign_net or foreign_net == 0) and (not indiv_net or indiv_net == 0):
            empty_count += 1

        inst_net = inst_net if inst_net else 0
        foreign_net = foreign_net if foreign_net else 0
        indiv_net = indiv_net if indiv_net else 0
        inst_str = inst_str if inst_str else 0
        foreign_str = foreign_str if foreign_str else 0

        print(f"{name:<15} {str(date):<15} {inst_net:>15,.0f} {foreign_net:>15,.0f} {indiv_net:>15,.0f} {inst_str:>15,.2f} {foreign_str:>15,.2f}")

    print("\n" + "=" * 160)
    print(f"Empty records (all zeros): {empty_count}/{len(result)}")
    print("\nExplanation:")
    print("- NetBuy: Net buying amount (positive = buying, negative = selling)")
    print("- Strength: Buying strength index (NetBuy / TradingValue * 100)")
    print("=" * 160)
