#!/usr/bin/env python3
"""
Interactive AI chat for AWS cost optimization
"""
import boto3
import subprocess
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
scans_table = dynamodb.Table('CostOptimizerScans')
costs_table = dynamodb.Table('CostAnalysisHistory')

# Store context for conversation
conversation_context = []

def get_data_summary():
    """Get current AWS data summary"""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    
    all_scans = []
    current_date = start_date
    
    while current_date <= end_date:
        try:
            response = scans_table.query(
                KeyConditionExpression='scan_date = :date',
                ExpressionAttributeValues={':date': str(current_date)}
            )
            all_scans.extend(response['Items'])
        except:
            pass
        current_date += timedelta(days=1)
    
    cost_response = costs_table.scan()
    cost_data = cost_response.get('Items', [])
    
    idle_scans = [s for s in all_scans if s.get('is_idle', False)]
    unique_instances = set(s['instance_id'] for s in all_scans)
    total_savings = sum(float(c.get('potential_savings', 0)) for c in cost_data)
    
    # Get instance details
    instance_details = {}
    for scan in all_scans:
        inst_id = scan['instance_id']
        if inst_id not in instance_details:
            instance_details[inst_id] = {
                'name': scan.get('instance_name', 'N/A'),
                'type': scan.get('instance_type', 'unknown'),
                'avg_cpu': float(scan.get('avg_cpu', 0)),
                'state': scan.get('instance_state', 'unknown')
            }
    
    return {
        'total_scans': len(all_scans),
        'idle_scans': len(idle_scans),
        'unique_instances': len(unique_instances),
        'idle_percentage': (len(idle_scans) / len(all_scans) * 100) if all_scans else 0,
        'potential_savings': total_savings,
        'instances': instance_details
    }

def query_ollama_with_context(user_question, data_summary):
    """Query Ollama with conversation context"""
    # Build context from data
    instance_info = "\n".join([
        f"- {inst_id}: {details['name']}, {details['type']}, {details['avg_cpu']:.2f}% CPU, {details['state']}"
        for inst_id, details in data_summary['instances'].items()
    ]) if data_summary['instances'] else "No instances currently running"
    
    system_context = f"""You are an AWS cost optimization expert assistant. You're helping analyze this AWS account:

Current Data:
- Total scans: {data_summary['total_scans']}
- Idle rate: {data_summary['idle_percentage']:.1f}%
- Potential savings: ${data_summary['potential_savings']:.2f}
- Instances: {data_summary['unique_instances']}

Instance Details:
{instance_info}

Answer the user's question based on this data. Be concise, specific, and actionable. If you don't have enough data, say so."""

    # Build conversation history
    conversation = system_context + "\n\n"
    for msg in conversation_context[-4:]:  # Last 4 exchanges for context
        conversation += f"{msg['role']}: {msg['content']}\n"
    conversation += f"User: {user_question}\nAssistant:"
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral', conversation],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main chat loop"""
    print("\n" + "="*70)
    print("🤖 AWS COST OPTIMIZER - AI ASSISTANT")
    print("="*70)
    print("\nAsk me anything about your AWS costs and usage!")
    print("Examples:")
    print("  • Why are my costs high?")
    print("  • What instances should I terminate?")
    print("  • How can I reduce my AWS bill?")
    print("  • What's the idle rate?")
    print("\nType 'exit' to quit, 'summary' for data overview\n")
    
    data_summary = get_data_summary()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! Your cost optimizer is still monitoring in the background.")
                break
            
            if user_input.lower() == 'summary':
                print(f"\n📊 Current Summary:")
                print(f"   Scans: {data_summary['total_scans']}")
                print(f"   Idle Rate: {data_summary['idle_percentage']:.1f}%")
                print(f"   Savings: ${data_summary['potential_savings']:.2f}")
                print(f"   Instances: {data_summary['unique_instances']}\n")
                continue
            
            # Add to conversation context
            conversation_context.append({'role': 'User', 'content': user_input})
            
            print("\n🤖 AI: ", end="", flush=True)
            response = query_ollama_with_context(user_input, data_summary)
            print(response + "\n")
            
            # Add AI response to context
            conversation_context.append({'role': 'Assistant', 'content': response})
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")

if __name__ == '__main__':
    main()