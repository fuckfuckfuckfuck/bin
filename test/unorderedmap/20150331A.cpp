#include <iostream>
//#include <hash_set>
//#include <boost/unordered_set.hpp>
#include <unordered_map>
#include <boost/assign/list_of.hpp>
using namespace boost;
using namespace std;

template<typename T>
void hash_func()
{
  using namespace boost::assign;
  T s = (list_of(1), 2, 3, 4, 5);   //初始化数据
  for (T::iterator p = s.begin(); p != s.end(); ++p) //使用迭代器遍历集合
    { cout<< *p<<" "; }
  cout<<endl;
  cout<<s.size()<<endl;
  s.clear();
  cout<<s.empty()<<endl;
  s.insert(8);
  s.insert(45);
  cout<<s.size()<<endl;
  cout<<*s.find(8)<<endl;
  s.erase(45);
}

int main() {
  hash_func<unordered_map<int> > ();
  system("pause");
  return 0;
}

